__CRON_DATE_AND_COMMAND_SEPARATOR_NUMBER = 5
__CRON_DATE_AND_COMMAND_SEPARATOR = " "


def get_cron_format_date(text, length=__CRON_DATE_AND_COMMAND_SEPARATOR_NUMBER):
    if text.startswith('# '):
        text = text[2:]
    return text[:find_nth_symbol_position_in_string(text.strip().replace('\\s+', '\\s'),
                                                    __CRON_DATE_AND_COMMAND_SEPARATOR,
                                                    length - 1)]


def get_cron_format_command(text, length=__CRON_DATE_AND_COMMAND_SEPARATOR_NUMBER):
    return text[find_nth_symbol_position_in_string(text,
                                                   __CRON_DATE_AND_COMMAND_SEPARATOR,
                                                   length - 1) + 1:]


def find_nth_symbol_position_in_string(string, substring, n):
    parts = string.split(substring, n + 1)

    return len(string) - len(parts[-1]) - len(substring)

