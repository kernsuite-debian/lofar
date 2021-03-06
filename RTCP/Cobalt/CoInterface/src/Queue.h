//# Queue.h:
//#
//#  Copyright (C) 2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef LOFAR_COINTERFACE_QUEUE_H
#define LOFAR_COINTERFACE_QUEUE_H

#ifdef USE_THREADS

#include <Common/Thread/Condition.h>
#include <Common/Thread/Mutex.h>
#include <CoInterface/TimeFuncs.h>
#include <CoInterface/RunningStatistics.h>

#include <deque>
#include <time.h>
#include <string>


namespace LOFAR {

  namespace Cobalt {

// Double-ended queue, thread-safe
template <typename T> class Queue
{
  public:
    // Create a named queue
    //
    // warn_remove_on_empty_queue: Emit a log warning if remove() is called when the queue is empty.
    // max_elements_on_append:     Emit a warning if append() overflowed the queue. -1 = disable.
    Queue(const std::string &name = "", bool warn_remove_on_empty_queue = false, int max_elements_on_append = -1);

    // Log queue statistics
    ~Queue();

    // Add an element to the back of the queue.
    //
    // If timed, this element is taken into account for statistics.
    //
    // Untimed items include:
    //   * Elements added to initially fill the queue, waiting for obs start.
    //   * Control elements, such as NULL.
    void     append(const T&, bool timed = true);

    // Put an element back to the front of the queue
    void     prepend(const T&);

    // Remove the front element; waits until `deadline' for an element,
    // and returns `null' if the deadline passed.
    T	       remove(const struct timespec &deadline = TimeSpec::universe_heat_death, T null = 0);

    unsigned size() const;
    bool     empty() const;
    struct timespec oldest() const;
    std::string name() const;

    // Reset all collected statistics.
    void reset_statistics();

  private:
    Queue(const Queue&);
    Queue& operator=(const Queue&);

  protected:
    const std::string itsName;

    // The time an element spent in a queue
    RunningStatistics retention_time;

    // The percentage of remove() calls on an empty queue
    RunningStatistics remove_on_empty_queue;

    // The average waiting time on remove() if the queue was empty
    RunningStatistics remove_wait_time;

    // The average queue size on append() (excluding the inserted element)
    RunningStatistics queue_size_on_append;

    const bool warn_remove_on_empty_queue;
    const int max_elements_on_append;

    struct Element {
      T value;
      struct timespec arrival_time;
    };

    mutable Mutex              itsMutex;
    Condition	                 itsNewElementAppended;
    std::deque<struct Element> itsQueue;

    // append() without grabbing itsMutex
    void     unlocked_append(const T&, bool timed);

    // pushes an item to the front of the queue ("prepend")
    void     push_front( const Element &e );

    // pushes an item to the back of the queue ("append")
    void     push_back( const Element &e );

    // pops the oldest item in the queue and returns it
    Element  pop_front();
};


template <typename T> Queue<T>::Queue(const std::string &name, bool warn_remove_on_empty_queue, int max_elements_on_append)
:
  itsName(name),
  retention_time("s"),
  remove_on_empty_queue("%"),
  remove_wait_time("s"),
  queue_size_on_append("elements"),
  warn_remove_on_empty_queue(warn_remove_on_empty_queue),
  max_elements_on_append(max_elements_on_append)
{
}


template <typename T> Queue<T>::~Queue()
{
  /*
   * Log statistics.
   *
   * Explanation and expected/ideal values:
   *
   * avg #elements on append:  Average size of the queue at append().
   *                      Q holding free items:           large
   *                      Q holding items for processing: 0-1
   *
   * queue empty on remove:    Percentage of calls to remove() that block
   *                      Q holding free items:           0%
   *                      Q holding items for processing: 100%
   *
   * remove wait time:        If queue wasn't empty on remove(), this is the average time before an item was appended
   *                      Q holding free items:           0
   *                      Q holding items for processing: >0
   *
   * element retention time:  The time an element spends between append() and remove()
   *                      Q holding free items:           large
   *                      Q holding items for processing: 0
   *
   */
  if (itsName != "") {
    if (max_elements_on_append >= 0 && queue_size_on_append.mean() >= static_cast<size_t>(max_elements_on_append)) {
      // This is a forward-feeding queue of elements holding data to be processed.
      //
      // Each element should disappear before the next one is offered. If not, the consumer of this queue
      // does not process fast enough. Possible reasons include:
      //    * The producer is blocked for resources (another queue, network, OS task scheduler, etc)
      //    * The producer processes too slowly (requested load too high, or need more parallellisation)

      LOG_WARN_STR("Queue " << itsName << " should always hold fewer than << max_elements_on_append << elements on append(). Queue had " << queue_size_on_append.mean() << " elements on append() (mean). At remove(), queue was empty " << remove_on_empty_queue.mean() << "% of the time. Time each element spent in queue: " << retention_time << ". In case of problems, look at the consume rate of this queue.");
    }

    if (warn_remove_on_empty_queue && remove_on_empty_queue.mean() > 0) {
      // This is a back-feeding queue of empty elements to be reused.
      //
      // If this queue is empty, the consumer wants to process but can't, because it has to wait for this queue.
      // This can incidentally happen, but is also a hint if performance is an issue. The thread replenishing this
      // queue (through append()) apparently does not do so fast enough. This in turn could be caused by earlier
      // problems, so looking for the first WARNING emitted by a remove() on an empty queue is key. Statistics of
      // queues logically placed earlier in the pipeline can provide insight as well.

      LOG_WARN_STR("Queue " << itsName << " should never be empty on remove(), always ready with data. Queue was empty " << remove_on_empty_queue.mean() << "% of the time. When empty, caller had to wait: " << remove_wait_time);
    }

    // Always log statistics for debugging, since it is invaluable information to debug incidental performance problems.
    LOG_INFO_STR("Queue " << itsName << ": avg #elements on append = " << queue_size_on_append.mean() << ", queue empty on remove = " << remove_on_empty_queue.mean() << "%, remove wait time = " << remove_wait_time.mean() << " s, element retention time: " << retention_time);
  }
}


template <typename T> inline void Queue<T>::append(const T& element, bool timed)
{
  ScopedLock scopedLock(itsMutex);

  unlocked_append(element, timed);
}


template <typename T> inline void Queue<T>::unlocked_append(const T& element, bool timed)
{
  Element e;

  // Copy the value to queue
  e.value        = element;

  // Note the time this element entered the queue
  e.arrival_time = timed ? TimeSpec::now() : TimeSpec::big_bang;

  // Record the queue size
  if (timed) queue_size_on_append.push(itsQueue.size());

  push_back(e);
}


template <typename T> inline void Queue<T>::prepend(const T& element)
{
  ScopedLock scopedLock(itsMutex);

  Element e;

  // Copy the value to queue
  e.value        = element;

  // We don't record an arrival time, since the element is likely
  // pushed back ("unget"). Recording an arrival time here would
  // screw up statistics.
  e.arrival_time = TimeSpec::big_bang;

  push_front(e);
}


template <typename T> inline void Queue<T>::push_front( const Element &e )
{
  itsQueue.push_front(e);

  itsNewElementAppended.signal();
}


template <typename T> inline void Queue<T>::push_back( const Element &e )
{
  itsQueue.push_back(e);

  itsNewElementAppended.signal();
}


template <typename T> inline typename Queue<T>::Element Queue<T>::pop_front()
{
  Element e = itsQueue.front();
  itsQueue.pop_front();

  return e;
}


template <typename T> inline T Queue<T>::remove(const struct timespec &deadline, T null)
{
  using namespace LOFAR::Cobalt::TimeSpec;

  // Return null if deadline passed
  if (TimeSpec::now() > deadline)
    return null;

  ScopedLock scopedLock(itsMutex);

  const bool beganEmpty = itsQueue.size() == 0;
  const struct timespec begin = TimeSpec::now();

  if (beganEmpty && warn_remove_on_empty_queue)
    LOG_WARN_STR("remove() called on empty queue: " << name());

  while (itsQueue.empty())
    if (!itsNewElementAppended.wait(itsMutex, deadline))
      return null;

  Element e = pop_front();

  const struct timespec end = TimeSpec::now();

  // Record waiting time if queue was not empty
  if (beganEmpty) {
    remove_wait_time.push(end - begin);
  }

  // Record whether we'll need to wait
  remove_on_empty_queue.push(beganEmpty ? 100.0 : 0.0);

  // Record the time this element spent in this queue
  if (e.arrival_time != TimeSpec::big_bang)
    retention_time.push(end - e.arrival_time);

  return e.value;
}


template <typename T> inline unsigned Queue<T>::size() const
{
  ScopedLock scopedLock(itsMutex);

  return itsQueue.size();
}


template <typename T> inline bool Queue<T>::empty() const
{
  return size() == 0;
}


template <typename T> inline struct timespec Queue<T>::oldest() const
{
  ScopedLock scopedLock(itsMutex);

  return itsQueue.empty() ? TimeSpec::now() : itsQueue.front().arrival_time;
}


template <typename T> inline std::string Queue<T>::name() const
{
  return itsName;
}

template <typename T> inline void Queue<T>::reset_statistics()
{
  retention_time.reset();
  remove_on_empty_queue.reset();
  remove_wait_time.reset();
  queue_size_on_append.reset();
}

} // namespace Cobalt

} // namespace LOFAR

#endif

#endif 
