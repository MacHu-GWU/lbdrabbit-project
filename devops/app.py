# -*- coding: utf-8 -*-

from lbdrabbit.example.app import MyAppConfig
from lbdrabbit import App


app_config = MyAppConfig()
app_config.PROJECT_NAME.set_value("lbdrabbit_example")
app_config.STAGE.set_value("dev")
app_config.HANDLER_MODULE_NAME.set_value("lbdrabbit.example.handlers")
app_config.S3_BUCKET_FOR_DEPLOY.set_value("eq-sanhe-for-everything")
app_config.AWS_PROFILE_FOR_DEPLOY.set_value("eq_sanhe")

app = App(import_name=__name__, app_config=app_config)
app.deploy()
