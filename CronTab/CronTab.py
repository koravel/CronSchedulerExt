from datetime import datetime
from croniter import croniter
from CronTab.CronJob import CronJob
from Utils import SchedulerUtils


class _JobTypes:
    Unreachable = "unreachable"
    Invalid = "invalid"


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
        try:
            with open(self.tabfile) as file_stream:
                lines = file_stream.readlines()
        except:
            raise FileNotFoundError()
        if len(lines) > 0:
            i = 1
            for line in lines:
                if len(line) > 0:
                    if line[0] == CronTab.__comment:
                        self.logger.log_info(CronTab.__comment_ignore_text.format(i, line))
                    else:
                        self.append_job(line)
                i += 1
        else:
            raise ValueError()

    def command_params_length(self, line):
        for command_type in self.__possible_croniter_format_usage_places:
            time_format = SchedulerUtils.get_cron_format_date(line, command_type)

            if croniter.is_valid(time_format):
                try:
                    croniter(time_format, datetime.now()).get_next()
                except:
                    raise ValueError(_JobTypes.Unreachable)
                return command_type
            else:
                raise ValueError(_JobTypes.Invalid)

    def append_job(self, line):
        try:
            length = self.command_params_length(line)
        except Exception as ex:
            if ex.args[0] == _JobTypes.Invalid:
                self.jobs.append(CronJob(_invalid=True))
                self.logger.log_warn(CronTab.__error_line.format(_JobTypes.Invalid, line))
            elif ex.args[0] == _JobTypes.Unreachable:
                self.jobs.append(CronJob(_unreachable=True))
                self.logger.log_warn(CronTab.__error_line.format(_JobTypes.Unreachable, line))
        else:
            job = CronJob(
                _formatted_period=SchedulerUtils.get_cron_format_date(line, length),
                _command=SchedulerUtils.get_cron_format_command(line, length)
            )

            # dummy set, change asap!
            job.setTimeout(self.settings["non_durable_job_timeout"])
            job.setInstancesAmount(self.settings["job_instances_amount"])
            job.setDurability(False)

            self.jobs.append(job)
