CRON_DATE_AND_COMMAND_SEPARATOR = " "
CRON_DATE_AND_COMMAND_SEPARATOR_NUMBER = 5
DEFAULT_EXCEPTION_TEXT = "An exception of type {0} occurred while {1}. {2}"
LOG_SEPARATOR = "---------------------------------"
FANCY_LOG_SEPARATOR = "*********************************"
COMMAND_LOG = "command {} will run {}'{} time at {}"


def get_numeric_suffix(i):
    if 0 < i < 4:
        return __numeric_suffix[i]
    return "th"


__numeric_suffix = {
    1: "st",
    2: "nd",
    3: "rd"
}

