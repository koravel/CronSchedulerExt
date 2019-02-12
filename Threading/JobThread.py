import os
import threading
from subprocess import TimeoutExpired

from crontab import open_pipe


class JobThread(threading.Thread):
    __started_text = "Job [{}] started"
    __disabled_text = "Job [{}] disabled"
    __reach_timeout_text = "Job [{}] has reached timeout limit"
    __executed_text = "Job [{}] executed"

    def __init__(self, job, logger, name):
        super(JobThread, self).__init__(name=name)
        self.job = job
        self.logger = logger

    def run(self):
        self.logger.log_info(JobThread.__started_text.format(self.job.command))

        # crontab execute code
        shell = os.environ.get('SHELL', '/bin/sh')
        (out, err) = open_pipe(shell, '-c', self.job.command).communicate(timeout=self.job.timeout)

        if err:
            self.logger.log_error(err.decode("utf-8"))
            if err is not TimeoutExpired:
                self.logger.log_warn(JobThread.__disabled_text.format(self.job))
                self.job.enabled = False
            else:
                self.logger.log_warn(JobThread.__reach_timeout_text.format(self.job))

        else:
            self.logger.log_info(JobThread.__executed_text.format(self.job.command))
