import time
from datetime import datetime
import queue

from CronTab.JobThread import JobThread


class Executer:
    __start_text = "Executer started"
    __reject_job_text = "Job [{}] rejected"
    __queue_reject_job_text = "Queue is full. " + __reject_job_text
    __put_job_in_queue_text = "Threads are busy. Put job [{}] in queue"
    __closing_threads_text = "Closing all running job treads"
    __threads_closed_text = "All running job threads closed"

    def __init__(self, crontab, logger, settings):
        self.crontab = crontab
        self.logger = logger
        self.settings = settings
        self.job_threads = []
        self.queue = queue.Queue(self.settings["queue_max_size"])

    #Author: Artyom Sysa
    def run(self, stop_event, refresh_event):
        self.logger.log_info(Executer.__start_text)
        while True:
            refresh_event.wait()
            for job in self.crontab.jobs:
                if job.enabled and not job.invalid and not job.unreachable:
                    if job.last_run is None:
                        job.last_run = datetime.now()
                    if self.settings["job_instances_amount"] < self.count_job_instances(job.command):

                        next_time = job.schedule(job.last_run).get_next()

                        now_tmp = datetime.now()
                        if next_time <= now_tmp:
                            job.last_run = now_tmp
                            if self.settings["threads_max"] < len(self.job_threads):
                                self.job_threads.append(JobThread(job, self.logger))
                                self.job_threads[-1].start()
                            elif self.settings["job_queue_enable"]:
                                if self.queue.full():
                                    self.logger.log_warn(Executer.__queue_reject_job_text.format(job))
                                else:
                                    self.logger.log_info(Executer.__put_job_in_queue_text.format(job))
                                    self.queue.put(JobThread(job, self.logger))
                            else:
                                self.logger.log_warn(Executer.__reject_job_text.format(job))

            if stop_event.is_set():
                self.stop_threads()
                return
            time.sleep(self.time_to_next_minute())

    def count_job_instances(self, command):
        amount = 0
        for thread in self.job_threads:
            if thread.command == command:
                amount += 1
        return amount

    # Author: Artyom Sysa
    def stop_threads(self):
        self.logger.log_info(Executer.__closing_threads_text)

        for jobThread in self.job_threads:
            jobThread.join()

        self.logger.info(Executer.__threads_closed_text)

    def time_to_next_minute(self):
        now = datetime.now()
        return 60 - now.second - now.microsecond/1000000
