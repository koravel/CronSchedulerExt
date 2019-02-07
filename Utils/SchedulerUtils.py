from Utils import Constants

#Author: Artyom Sysa
def get_cron_format_date(text, length=Constants.CRON_DATE_AND_COMMAND_SEPARATOR_NUMBER):
    if text.startswith('# '):
        text = text[2:]
    return text[:find_nth_symbol_position_in_string(text.strip().replace('\\s+', '\\s'),
                                                    Constants.CRON_DATE_AND_COMMAND_SEPARATOR,
                                                    length - 1)]

#Author: Artyom Sysa
def get_cron_format_command(text, lenght=Constants.CRON_DATE_AND_COMMAND_SEPARATOR_NUMBER):
    return text[find_nth_symbol_position_in_string(text,
                                                   Constants.CRON_DATE_AND_COMMAND_SEPARATOR,
                                                   lenght - 1) + 1:]

#Author: Artyom Sysa
def find_nth_symbol_position_in_string(string, substring, n):
    parts = string.split(substring, n + 1)

    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)
