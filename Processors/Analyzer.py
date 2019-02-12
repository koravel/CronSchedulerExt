from datetime import datetime

import PathProvider
import Utils
from Utils import Constants


class Analyzer:
    __analyzing_text = "Analyzing {} file. {} iterations will be output for each job"
    __analysis_complete_text = "Analysis complete"
    __wrong_job_text = "wrong job style on line {}"
    __unreachable_job_text = 'unreachable job on line {}'
    __run_command_text = "run time for command {}"
    __command_log = "command {} will run {}'{} time at {}"

    def __init__(self, crontab, iterations_amount, logger):
        self.iterations_amount = iterations_amount
        self.crontab = crontab
        self.__line = 1
        self.logger = logger

    @staticmethod
    def get_next_iteration(schedule):
        return schedule.get_next()

    def analyze_single(self, job):
        self.logger.log_info(Constants.LOG_SEPARATOR)
        if job.invalid:
            self.logger.log_warn(Analyzer.__wrong_job_text.format(self.__line))
        elif job.unreachable:
            self.logger.log_warn(Analyzer.__unreachable_job_text.format(self.__line))
        else:
            self.logger.log_info(Analyzer.__run_command_text.format(job.command))
            schedule = job.schedule(datetime.now())
            for i in range(1, self.iterations_amount + 1):
                self.logger.log_info(Analyzer.__command_log.format(job.command, i, Utils.get_numeric_suffix(i),
                                                                  Analyzer.get_next_iteration(schedule)))
        self.__line += 1

    def analyze_all(self):
        self.logger.log_info(Utils.Constants.FANCY_LOG_SEPARATOR)
        self.logger.log_info(Analyzer.__analyzing_text.format(PathProvider.pathes["TAB"].location, self.iterations_amount))

        for job in self.crontab.jobs:
            self.analyze_single(job)
            self.logger.log_info(Constants.LOG_SEPARATOR)

        self.logger.log_info(Analyzer.__analysis_complete_text)
        self.logger.log_info(Utils.Constants.FANCY_LOG_SEPARATOR)
