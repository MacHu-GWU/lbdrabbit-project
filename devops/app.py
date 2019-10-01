# -*- coding: utf-8 -*-

from lbdrabbit.example.app import app, MyAppConfig


app_config = MyAppConfig()
app_config.PROJECT_NAME.set_value("lbdrabbit_example")
app_config.STAGE.set_value("dev")
app_config.HANDLER_MODULE_NAME.set_value("lbdrabbit.example.handlers")
app.config = app_config
app.deploy()
