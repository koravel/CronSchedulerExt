import multiprocessing.dummy
import queue
import threading
from threading import Thread


class ThreadsManager:
    __threads_amount_text = "Amount of threads cannot be lower than 5"
    __thread_started_text = "Thread {} started"
    __thread_stopped_text = "Thread {} stopped"

    def __init__(self, logger, settings, threads_max_amount):
        self.logger = logger
        self.settings = settings
        if threads_max_amount < 5:
            logger.log_fatal(ThreadsManager.__threads_amount_text)
            raise MemoryError()
        self.threads_max_amount = threads_max_amount
        self.stop_event = threading.Event()
        self.threads = []
        self.queue = queue.Queue(self.settings["queue_max_size"])

    def stop_thread(self, name):
        for thread in self.threads:
            if thread.name == name:
                thread.join()
                self.logger.log_info(ThreadsManager.__thread_stopped_text.format(thread.name))

    def stop_all_threads(self):
        for thread in self.threads:
            thread.join()
            self.logger.log_info(ThreadsManager.__thread_stopped_text.format(thread.name))

    def add_target(self, target):
        if len(self.threads) < self.threads_max_amount:
            self.threads.append(Thread(target=target))
            return True
        else:
            raise OverflowError()

    def add_thread(self, thread):
        if len(self.threads) < self.threads_max_amount:
            self.threads.append(thread)
            return True
        else:
            raise OverflowError()

    def start_thread(self, name):
        for thread in self.threads:
            if thread.name == name and not thread.isAlive():
                thread.start()
                self.logger.log_info(ThreadsManager.__thread_started_text.format(thread.name))

    def add_thread_to_queue(self, thread):
        if self.settings["job_queue_enable"]:
            if self.queue.full():
                raise OverflowError()
            else:
                self.queue.put(thread)
                return True
        else:
            raise OverflowError()

    def contains_thread(self, name):
        for thread in self.threads:
            if thread.name == name:
                return True
        return False
