# -*- coding: utf-8 -*-

from configirl import Constant, Derivable, ConfigClass


class AppConfig(ConfigClass):
    pass


class App(object):
    def __init__(self,
                 import_name: str,
                 app_config: AppConfig = None):
        self.import_name = import_name

        if app_config is None:
            app_config = AppConfig()

        self.config = app_config
