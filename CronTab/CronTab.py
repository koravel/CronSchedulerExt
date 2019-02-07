from datetime import datetime
from croniter import croniter
from CronTab.CronJob import CronJob
from Utils import SchedulerUtils


class CronTab:
    __comment = "#"
    __comment_ignore_text = "Ignore line [{}]:'{}' - comment"
    __error_line = "{} job format on line {}"
    __error_tabfile = "tabfile is {}"
    __possible_croniter_format_usage_places = [6, 5]

    def __init__(self, logger, settings, tabfile=None):
        self.tabfile = tabfile
        self.logger = logger
        self.settings = settings
        self.jobs = []
        self.__read_tabfile()

    def __read_tabfile(self):
        lines = None
        with open(self.tabfile) as file_stream:
            lines = file_stream.readlines()
        if lines is not None:
            if len(lines) > 0:
                i = 1
                for line in lines:
                    if len(line) > 0:
                        if line[0] == CronTab.__comment:
                            self.logger.log_info(CronTab.__comment_ignore_text.format(i, line))
                        else:
                            self.append_job(line)
                    i += 1
                return 0
            else:
                raise ValueError()
        else:
            raise FileNotFoundError()

    # Author: Artyom Sysa
    def is_job_format_line_valid(self, line):
        for i in self.__possible_croniter_format_usage_places:
            time_format = SchedulerUtils.get_cron_format_date(line, i)
            if croniter.is_valid(time_format):
                try:
                    croniter(time_format, datetime.now()).get_next()
                except:
                    # unreachable line return params
                    return False, -1
                # valid line return params
                return True, i
        # invalid line return params
        return False, -2

    def append_job(self, line):
        result, length = self.is_job_format_line_valid(line)

        if result:
            job = CronJob(
                _formatted_period=SchedulerUtils.get_cron_format_date(line, length),
                _command=SchedulerUtils.get_cron_format_command(line, length)
            )

            #dummy set, change asap!
            job.setTimeout(self.settings["non_durable_job_timeout"])
            job.setInstancesAmount(self.settings["job_instances_amount"])
            job.setDurability(False)

            self.jobs.append(job)
            return 0
        else:
            if length == -2:
                self.jobs.append(CronJob(_invalid=True))
                self.logger.log_warn(CronTab.__error_line.format("invalid", line))
                return 1
            else:
                self.jobs.append(CronJob(_unreachable=True))
                self.logger.log_warn(CronTab.__error_line.format("unreachable", line))
                return 2
