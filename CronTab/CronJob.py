from datetime import datetime
from croniter import croniter


class CronJob:
    def __init__(self, _command='', _formatted_period='', _durable=False, _invalid=False, _unreachable=False):
        self.command = _command.replace('\n', '')
        self.formatted_period = _formatted_period
        self.durable = _durable
        self.invalid = _invalid
        self.unreachable = _unreachable
        self.last_run = None
        self.enabled = True

    def setTimeout(self, timeout):
        self.timeout = timeout

    def setInstancesAmount(self, amount):
        self.instances_amount = amount

    def setDurability(self, isDurable):
        self.durable = isDurable

    def schedule(self, date_from):
        return croniter(self.formatted_period, date_from, ret_type=datetime, day_or=False)
