import Router


class Settings:
    settings = dict()

    def __init__(self, writer, reader):
        Settings.writer = writer
        Settings.reader = reader

    @staticmethod
    def save():
        try:
            Settings.writer.write(Settings.settings, Router.routes["SETTINGS"].location)
        except Exception as ex:
            raise ex

    @staticmethod
    def load():
        try:
            Settings.settings = Settings.reader.read(Router.routes["SETTINGS"].location)
        except Exception as ex:
            Settings.set_default()
            raise ex


    @staticmethod
    def set(**kwargs):
        Settings.settings = kwargs
        Settings.save()

    @staticmethod
    def set_default():
        Settings.set(
            log_level=4,
            analyzer_enable=False,
            analyze_at_startup_only=True,
            analyzer_iterations_amount=10,
            analyzer_period=60,
            log_analysis=True,
            tabfile_refresh=True,
            tabfile_refresh_time=60,
            threads_max=10,
            job_queue_enable=True,
            queue_max_size=10,
            non_durable_job_timeout=60,
            job_instances_amount=1,
            queue_priority_enable=False
        )
