import logging
from datetime import datetime, timedelta
from threading import Thread
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

logger = logging.getLogger()

class PipeReader:
    '''
    helper class to do non-blocking readline calls to a subprocess stdput or stderr pipe.
    '''
    def __init__(self, pipe):
        self.__line_buffer = ''
        self.__queue = Queue()
        self.__thread = Thread(target=PipeReader.enqueue_output, args=(pipe, self.__queue))
        self.__thread.daemon = True # thread dies with the program
        self.__thread.start()

    @staticmethod
    def enqueue_output(pipe, queue):
        try:
            for line in iter(pipe.readline, b''):
                queue.put(line)
        except Exception as e:
            logger.error(e)

    def __fill_line_buffer(self, timeout=None):
        start = datetime.now()
        while timeout==None or datetime.now() - start <= timedelta(seconds=timeout):
            try:
                result = self.__queue.get(True, timeout)
                if result:
                    self.__line_buffer += result
            except Empty:
                pass

    def readline(self, timeout=None):
        self.__fill_line_buffer(timeout)

        endline_idx = self.__line_buffer.find('\n')

        if endline_idx > -1:
            line = self.__line_buffer[:endline_idx]
            self.__line_buffer = self.__line_buffer[endline_idx+1:]
            return line
        return ''

    def readlines(self, timeout=None):
        self.__fill_line_buffer(timeout)

        last_line_end_idx = self.__line_buffer.rfind('\n')
        head = self.__line_buffer[:last_line_end_idx]
        self.__line_buffer = self.__line_buffer[last_line_end_idx:]

        lines = [l for l in head.split('\n') if l]

        return lines
