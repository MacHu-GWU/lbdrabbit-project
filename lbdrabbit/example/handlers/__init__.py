# -*- coding: utf-8 -*-

from lbdrabbit.config_inherit import LbdFuncConfig, ApiMethodIntType
from lbdrabbit.example import cf
from lbdrabbit.example.app_config_init import app_config

__lbd_func_config__ = LbdFuncConfig()
__lbd_func_config__.param_env_name = cf.param_env_name

__lbd_func_config__.lbd_func_yes = True
__lbd_func_config__.lbd_func_code = cf.lambda_code
__lbd_func_config__.lbd_func_iam_role = cf.iam_role
__lbd_func_config__.lbd_func_runtime = "python3.6"
__lbd_func_config__.lbd_func_layers = app_config.LAMBDA_LAYER_ARN.get_value()

__lbd_func_config__.apigw_restapi = cf.rest_api
__lbd_func_config__.apigw_resource_yes = True

__lbd_func_config__.apigw_method_yes = True
__lbd_func_config__.apigw_method_authorization_type = "CUSTOM"
__lbd_func_config__.apigw_method_authorizer = LbdFuncConfig.get_authorizer_id("auth")
__lbd_func_config__.apigw_method_enable_cors_yes = True

__lbd_func_config__.apigw_authorizer_token_type_header_field = "auth"
