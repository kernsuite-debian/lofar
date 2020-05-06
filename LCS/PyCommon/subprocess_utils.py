import logging
from datetime import datetime, timedelta
from time import sleep
from threading import Thread, Event
from subprocess import Popen, PIPE, check_output
from collections import namedtuple
try:
    from queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

logger = logging.getLogger()

class SubprocessTimoutError(TimeoutError):
    '''an error class indication that the running subprocess to longer than expected to complete'''
    pass

def wrap_composite_command(cmd):
    """
    wrap the whole commandline like so: "<cmd>"
    so, for example, multiple ';'-seperated commands are interpreted as one single argument for ssh for example
    :param cmd: string of list of strings with the commandline to be executed. May or may not contain ';'
    :return: the encapsulated command
    """
    return '''"%s" ''' % (cmd if isinstance(cmd, str) else ' '.join(cmd))


def _convert_bytes_tuple_to_strings(bytes_tuple):
    """Helper function for subprocess.communicate() and/or subprocess.check_output which changed from python2 to python3.
    This function returns the bytes in the bytes_tuple_tuple to utf-8 strings.
    You can use this to get the "normal" python2 subprocess behaviour back for functions like check_output and/or communicate."""
    return tuple('' if x is None
                 else x.decode('UTF-8') if isinstance(x, bytes)
                 else x
                 for x in bytes_tuple)

def communicate_returning_strings(proc, input=None):
    """Helper function for subprocess.communicate() which changed from python2 to python3.
    This function waits for the subprocess to finish and returns the stdout and stderr as utf-8 strings, just like python2 did."""
    return _convert_bytes_tuple_to_strings(proc.communicate(input=input))

def check_output_returning_strings(*popenargs, timeout=None, **kwargs):
    """Helper function for subprocess.check_output(...) which changed from python2 to python3.
    This function waits for the subprocess to finish and returns the stdout and stderr as utf-8 strings, just like python2 did."""
    output = check_output(*popenargs, timeout=timeout, **kwargs)
    if isinstance(output, tuple):
        return _convert_bytes_tuple_to_strings()
    if isinstance(output, bytes):
        return output.decode('UTF-8')
    return output

def execute_in_parallel(cmd_lists, gather_stdout_stderr: bool=True, timeout=3600, max_parallel=32):
    """
    Execute all commands in the cmd_lists in parallel, limited to max_parallel concurrent processes.
    :param list cmd_lists: a list of subprocess-cmd-list's
    :param bool gather_stdout_stderr: when True, then do gather the output from stdout and stderr,
                                      else stdout and stderr are 'mixed in' this program's stdout and stderr.
    :param int timeout: time out after this many seconds
    :param int max_parallel: maximum number of concurrent executed commands.
    :raises a SubprocessTimoutError if any of the commands time out
    :return: list with the results in the same order as the cmd_lists. Each result contains the returncode, stdout and stderr.
    """
    procs = []
    start = datetime.utcnow()
    for cmd_list in cmd_lists:
        # first check how many procs are already running in parallel
        # wait a little while we exceed the number of max_parallel procs
        # or else continue starting procs
        while True:
            num_running = len([proc for proc in procs if proc.poll() is None])
            if num_running < max_parallel:
                break
            sleep(0.01)

        # not limited by the number of parallel procs (anymore)
        # so, start a new proc
        logger.info('Executing %s', ' '.join(cmd_list))
        if gather_stdout_stderr:
            proc = Popen(cmd_list, stdout=PIPE, stderr=PIPE)
        else:
            proc = Popen(cmd_list, bufsize=-1)
        procs.append(proc)
        sleep(0.01)

    try:
        while not all(proc.poll() is not None for proc in procs):
            if datetime.utcnow() - start >= timedelta(seconds=timeout):
                raise SubprocessTimoutError("Timeout while waiting for subprocess")
            sleep(0.01)

    except SubprocessTimoutError as e:
        logger.error(e)
        for proc in procs:
            if proc.poll() is None:
                proc.kill()
        raise

    PopenResult = namedtuple('PopenResult', ['returncode', 'stdout', 'stderr'])

    results = [PopenResult(p.returncode,
                           p.stdout.read().decode('utf-8').strip() if gather_stdout_stderr else None,
                           p.stderr.read().decode('utf-8').strip() if gather_stdout_stderr else None)
               for p in procs]

    # log results of commands
    for cmd_list, result in zip(cmd_lists, results):
        logger.debug("Results for cmd: %s\n  returncode=%s\n  stdout=%s\n  stderr=%s",
                     " ".join(cmd_list),
                     result.returncode, result.stdout, result.stderr)
    return results

class PipeReader:
    '''
    helper class to do non-blocking readline calls to a subprocess stdout or stderr pipe.
    '''
    def __init__(self, pipe, name=None):
        self.__line_buffer = ''
        self.__name = name
        self.__pipe = pipe
        self.__queue = Queue()
        self.__stop_event = Event()
        self.__thread = None

    def start(self):
        self.stop()

        self.__thread = Thread(target=self.__enqueue_output,
                               name='PipeReader_thread_%s' % (self.__name,))
        self.__thread.daemon = True # thread dies with the program
        logger.debug("starting %s", self.__thread.name)
        self.__thread.start()

    def stop(self):
        if self.__thread and self.__thread.is_alive():
            logger.debug("stopping %s", self.__thread.name)
            self.__stop_event.set()
            self.__thread.join()
            logger.info("stopped %s", self.__thread.name)
            self.__thread = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __enqueue_output(self):
        try:
            for line in iter(self.__pipe.readline, b''):
                self.__queue.put(line)
                if self.__stop_event.is_set():
                    self.__stop_event.clear()
                    break
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
