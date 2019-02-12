import signal
import sys
import threading
import time

import PathProvider
from CronTab.CronTab import CronTab
from Processors.Executer import Executer
from Threading.ThreadsManager import ThreadsManager
from Utils.Settings import Settings
from Utils.Logger import Logger
from CronIO.JsonWriter import JSONWriter
from CronIO.JsonReader import JSONReader
from CronIO.FileWriter import FileWriter
from Processors.Analyzer import Analyzer
from threading import Lock, Thread


class _AppStatus:
    NORMAL_EXIT = 0
    INIT_SETTINGS_ERROR = -2
    TABFILE_NOT_FOUND_ERROR = -3
    SAVING_SETTINGS_ERROR = -4


class App:
    __tabfile_load_text = "loading tabfile"
    __settings_load_text = "loading settings"
    __wait_tabfile_data_text = "Tabfile is empty. Wait for new data..."
    __tabfile_loaded_text = "tabfile data successfully loaded"
    __app_start_text = "Starting up application..."
    __app_started_text = "Application started successfully"
    __app_closing_text = "Clothing application..."
    __app_closed_text = "Application closed successfully"
    __run_executer_text = "Starting up Executer..."
    __stop_executer_text = "Excuter stopped"
    __run_analyzer_text = "Starting up Analyzer..."
    __stop_analyzer_text = "Analyzer stopped"
    __run_refresher_text = "Starting up tabfile refresh..."
    __stop_refresher_text = "Tabfile refresh stopped"
    __default_exception_text = "An exception of type {0} occurred while {1}. {2}"

    def __init__(self):
        self.init_components()

        self.threads_manager = ThreadsManager(self.logger, self.settings, self.settings["threads_max"])
        self.init_threads()
        self.refresh_event = threading.Event()

    def init_threads(self):
        self.threads_manager.add_thread(threading.Thread(target=self.run_executer, name="executer"))
        self.threads_manager.add_thread(threading.Thread(target=self.__refresh_crontab, name="refresher"))
        self.threads_manager.add_thread(threading.Thread(target=self.analysis_execution, name="analyzer"))

    @staticmethod
    def __get_formatted_error(ex, text, additional_info=""):
        return App.__default_exception_text.format(type(ex).__name__, text, additional_info)

    def __init_settings(self):
        try:
            settings = Settings(JSONWriter, JSONReader)
            settings.load()
            self._settings_obj = settings
            self.settings = settings.settings
        except Exception as ex:
            self.threads_manager.stop_event.set()
            self.logger.log_fatal(App.__get_formatted_error(ex, App.__settings_load_text))
            self.close_application(_AppStatus.INIT_SETTINGS_ERROR)
        else:
            self.logger.log_level = self.settings["log_level"]
            self.logger.log_info(App.__app_started_text)

    def __refresh_crontab(self):
        self.logger.log_info(App.__run_refresher_text)
        file_empty = False
        empty_delay = 1

        while True:
            self.refresh_event.clear()
            try:
                self.cron = CronTab(tabfile=PathProvider.pathes["TAB"].location, logger=self.logger, settings=self.settings)
            except ValueError as ex:
                if not file_empty:
                    self.logger.log_error(App.__get_formatted_error(ex, App.__tabfile_load_text,
                                                                    App.__wait_tabfile_data_text))
                    file_empty = True
                time.sleep(empty_delay)
            except FileNotFoundError as ex:
                self.logger.log_fatal(App.__get_formatted_error(ex, App.__tabfile_load_text))
                self.close_application(_AppStatus.TABFILE_NOT_FOUND_ERROR)
            else:
                self.logger.log_info(App.__tabfile_loaded_text)
                self.refresh_event.set()
                if self.settings["tabfile_refresh"]:
                    time.sleep(self.settings["tabfile_refresh_time"])
                else:
                    break
            if self.threads_manager.stop_event.is_set():
                return

    def init_components(self):
        PathProvider.load()
        self.logger = Logger(FileWriter, PathProvider.pathes["LOG"].location)
        self.logger.log_info(App.__app_start_text)
        self.__init_settings()

    def analyze_once(self):
        self.refresh_event.wait()
        analysis_logger = self.logger
        if not self.settings["log_analysis"]:
            analysis_logger = Logger(FileWriter, PathProvider.pathes["ANALYSIS"].location)
        Analyzer(self.cron, self.settings["analyzer_iterations_amount"], analysis_logger).analyze_all()

    def analysis_execution(self):
        self.logger.log_info(App.__run_analyzer_text)
        if self.settings["analyze_at_startup_only"]:
            self.analyze_once()
        else:
            while True:
                self.analyze_once()
                time.sleep(self.settings["analyzer_period"])

    def run_executer(self):
        self.logger.log_info(App.__run_executer_text)
        self.refresh_event.wait()
        self.executer = Executer(self.cron, self.logger, self.settings, self.threads_manager)
        self.executer.run(self.refresh_event)

    def close_application(self, code):
        self.logger.log_info(App.__app_closing_text)
        PathProvider.save()
        try:
            self._settings_obj.save()
        except Exception as ex:
            self.logger.log_fatal(App.__get_formatted_error(ex, ex.args))
            sys.exit(_AppStatus.SAVING_SETTINGS_ERROR)
        else:
            self.logger.log_info(App.__app_closed_text)
            sys.exit(code)

    def sigint_handler(self, signum, frame):
        self.threads_manager.stop_event.set()
        self.threads_manager.stop_all_threads()

        self.close_application(_AppStatus.NORMAL_EXIT)

    def refresh(self):
        self.threads_manager.start_thread("refresher")

    def execute(self):
        self.threads_manager.start_thread("executer")

    def analyze(self):
        if self.settings["analyzer_enable"]:
            self.threads_manager.start_thread("analyzer")


if __name__ == '__main__':
    app = App()
    signal.signal(signal.SIGINT, app.sigint_handler)
    app.refresh()
    app.execute()
    app.analyze()
