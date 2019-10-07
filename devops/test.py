# -*- coding: utf-8 -*-

import boto3
from lbdrabbit.const import VALID_LBD_HANDLER_FUNC_NAME_LIST, DEFAULT_LBD_HANDLER_FUNC_NAME
from lbdrabbit.lbd_func_config.base import config_inherit_handler
from lbdrabbit.lbd_func_config.lbd_func_config import (
    LbdFuncConfig,
    DEFAULT_LBD_FUNC_CONFIG_FIELD,
    lbd_func_config_value_handler,
    template_creation_handler,
)
from lbdrabbit.example.app_config_init import app_config
from lbdrabbit.example.cf import template
from lbdrabbit.stack import upload_cf_template, deploy_stack

module_name = "lbdrabbit.example.handlers"
config_inherit_handler(
    module_name=module_name,
    config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
    config_class=LbdFuncConfig,
    valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
)

lbd_func_config_value_handler(
    module_name=module_name,
    config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
    config_class=LbdFuncConfig,
    valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
    default_lbd_handler_name=DEFAULT_LBD_HANDLER_FUNC_NAME,
)

template_creation_handler(
    module_name=module_name,
    config_field=DEFAULT_LBD_FUNC_CONFIG_FIELD,
    config_class=LbdFuncConfig,
    valid_func_name_list=VALID_LBD_HANDLER_FUNC_NAME_LIST,
    template=template,
)

template.update_tags(dict(
    Project=app_config.PROJECT_NAME_SLUG.get_value(),
    Stage=app_config.STAGE.get_value(),
    EnvName=app_config.ENVIRONMENT_NAME.get_value(),
))
template.create_resource_type_label()
template.to_file("master.json")

print("We have {} resources in template".format(len(template.resources)))

boto_ses = boto3.session.Session(profile_name=app_config.AWS_PROFILE_FOR_DEPLOY.get_value())

template_url = upload_cf_template(
    boto_ses=boto_ses,
    template_content=template.to_json(),
    bucket_name=app_config.S3_BUCKET_FOR_DEPLOY.get_value(),
    prefix="cloudformation/upload"
)

cf_config_data = app_config.to_cloudformation_config_data()
stack_parameters = [
    {
        "ParameterKey": key,
        "ParameterValue": cf_config_data[key],
    }
    for key in template.parameters
    if cf_config_data.get(key) is not None
]

deploy_stack(
    boto_ses=boto_ses,
    stack_name=app_config.STACK_NAME.get_value(),
    template_url=template_url,
    stack_tags=[],
    stack_parameters=stack_parameters,
    # execution_role_arn,
)
