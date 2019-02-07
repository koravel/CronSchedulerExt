import os
import signal
import sys
import threading
import time
from datetime import datetime

import Utils, Router, Utils.Constants
from CronTab.CronTab import CronTab
from Processors.Executer import Executer
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
    __run_executer_text = "Starting up Executer..."
    __stop_executer_text = "Excuter stopped"

    def __init__(self):
        self.init_components()

        self.stop_event = threading.Event()
        self.refresh_event = threading.Event()
        self.executer_thread = threading.Thread(target=self.run_executer)
        self.refresh_thread = threading.Thread(target=self.__refresh_crontab)
        self.analyzer_thread = threading.Thread(target=self.analysis_execution)

    @staticmethod
    def __get_formatted_error(ex, text, additional_info=""):
        return Utils.Constants.DEFAULT_EXCEPTION_TEXT.format(type(ex).__name__, text, additional_info)

    def __init_settings(self):
        try:
            settings = Settings(JSONWriter, JSONReader)
            settings.load()
            self.settings = settings.settings
        except Exception as ex:
            self.logger.log_fatal(App.__get_formatted_error(ex, App.__settings_load_text))
            self.close_application(_AppStatus.INIT_SETTINGS_ERROR)
        else:
            self.logger.log_level = self.settings["log_level"]
            self.logger.log_info(App.__app_started_text)

    def __refresh_crontab(self):
        file_empty = False
        empty_delay = 1

        while True:
            self.refresh_event.clear()
            try:
                self.cron = CronTab(tabfile=Router.routes["TAB"].location, logger=self.logger, settings=self.settings)
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
            if self.stop_event.is_set():
                return

    def init_components(self):
        self.logger = Logger(FileWriter, Router.routes["LOG"].location)
        self.logger.log_info(App.__app_start_text)
        self.__init_settings()

    def analyze_once(self):
        self.refresh_event.wait()
        analysis_logger = self.logger
        if not self.settings["log_analysis"]:
            analysis_logger = Logger(FileWriter, Router.routes["ANALYSIS"].location)
        Analyzer(self.cron, self.settings["analyzer_iterations_amount"], analysis_logger).analyze_all()

    def analysis_execution(self):
        if self.settings["analyze_at_startup_only"]:
            self.analyze_once()
        else:
            while True:
                self.analyze_once()
                time.sleep(self.settings["analyzer_period"])

    def run_executer(self):
        self.logger.log_info(App.__run_executer_text)
        self.refresh_event.wait()
        self.executer = Executer(self.cron, self.logger, self.settings)
        self.executer.run(self.stop_event, self.refresh_event)

    def close_application(self, code):
        try:
            self.settings.save()
        except Exception as ex:
            self.logger.log_fatal(App.__get_formatted_error(ex, ex.args))
            sys.exit(_AppStatus.SAVING_SETTINGS_ERROR)
        sys.exit(code)

    def sigint_handler(self, signum, frame):
        self.stop_event.set()
        self.executer_thread.join()
        self.refresh_thread.join()

        self.logger.log_info(App.__stop_executer_text)
        self.close_application(_AppStatus.NORMAL_EXIT)

    def refresh(self):
        if not self.refresh_thread.isAlive():
            self.refresh_thread.start()

    def execute(self):
        if not self.executer_thread.isAlive():
            self.executer_thread.start()

    def analyze(self):
        if self.settings["analyzer_enable"]:
            if not self.analyzer_thread.isAlive():
                self.analyzer_thread.start()


if __name__ == '__main__':
    Router.load()
    app = App()
    signal.signal(signal.SIGINT, app.sigint_handler)
    app.refresh()
    app.execute()
    app.analyze()
    Router.save()
