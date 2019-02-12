import time
from datetime import datetime

from Threading.JobThread import JobThread


class Executer:
    __start_text = "Executer started"
    __reject_job_text = "Job [{}] rejected"
    __queue_reject_job_text = "Queue is full. " + __reject_job_text
    __put_job_in_queue_text = "Threads are busy. Put job [{}] in queue"
    __closing_threads_text = "Closing all running job treads"
    __threads_closed_text = "All running job threads closed"

    def __init__(self, crontab, logger, settings, threads_manager):
        self.crontab = crontab
        self.logger = logger
        self.settings = settings
        self.threads_manager = threads_manager

    def run(self, refresh_event):
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
                            job_name = "job[{} {}]".format(job.formatted_period, job.command)
                            if self.threads_manager.contains_thread(job_name):
                                job_name += "_"
                            try:
                                self.threads_manager.add_thread(JobThread(job, self.logger, job_name))
                            except:
                                try:
                                    self.threads_manager.add_thread_to_queue(JobThread(job, self.logger, job_name))
                                except:
                                    self.logger.log_warn(Executer.__queue_reject_job_text.format(job))
                                else:
                                    self.logger.log_info(Executer.__put_job_in_queue_text.format(job))
                            else:
                                self.threads_manager.start_thread(job_name)

            time.sleep(self.time_to_next_minute())

    def count_job_instances(self, command):
        amount = 0
        for thread in self.threads_manager.threads:
            if hasattr(thread, "job"):
                if thread.job.command == command:
                    amount += 1
        return amount

    def time_to_next_minute(self):
        now = datetime.now()
        return 60 - now.second - now.microsecond/1000000
