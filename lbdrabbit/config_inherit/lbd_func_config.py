# -*- coding: utf-8 -*-

import typing
import attr
from importlib import import_module
from picage import Package
from troposphere_mate import Template, Parameter, Tags, Ref, GetAtt, Sub
from troposphere_mate import awslambda, apigateway
from troposphere_mate import slugify, camelcase

from .base import BaseConfig, REQUIRED, NOTHING, walk_lbd_handler


DEFAULT_LBD_FUNC_CONFIG_FIELD = "__lbd_func_config__"


class ApiMethodIntType:
    rest = "rest"
    rpc = "rpc"
    html = "html"


@attr.s
class LbdFuncConfig(BaseConfig):
    """
    Lambda Function Level Config.

    Every child function under a resource inherits :class:`ResourceConfig``.

    **中文文档**


    """
    function_name = attr.ib(default=REQUIRED)  # type: str
    description = attr.ib(default=NOTHING)  # type: str
    memory_size = attr.ib(default=NOTHING)  # type: int
    iam_role = attr.ib(default=REQUIRED)  # type: Parameter
    timeout = attr.ib(default=NOTHING)  # type: int
    runtime = attr.ib(default=REQUIRED)  # type: str
    code = attr.ib(default=REQUIRED)  # type: awslambda.Code
    layers = attr.ib(default=NOTHING)  # type: list
    reserved_concurrency = attr.ib(default=NOTHING)  # type: int
    environment_vars = attr.ib(default=NOTHING)  # type: awslambda.Environment
    kms_key_arn = attr.ib(default=NOTHING)  # type: str
    vpc_config = attr.ib(default=NOTHING)  # type: awslambda.VPCConfig
    dead_letter_config = attr.ib(default=NOTHING)  # type: awslambda.DeadLetterConfig
    tracing_config = attr.ib(default=NOTHING)  # type: awslambda.TracingConfig

    lbd_func_metadata = attr.ib(default=NOTHING)  # type: dict
    lbd_func_tags = attr.ib(default=NOTHING)  # type: Tags

    apigw_resource_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_restapi = attr.ib(default=NOTHING)  # type: typing.Union[apigateway.RestApi, Ref, str]
    apigw_resource_path_part = attr.ib(default=NOTHING)  # type: str

    apigw_method_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_method_int_type = attr.ib(default=NOTHING)  # type: str

    _py_module = attr.ib(default=NOTHING)
    _py_function = attr.ib(default=NOTHING)

    _default = dict(
        memory_size=128,
        timeout=3,
        apigw_resource_yes=False,
        apigw_method_yes=False,
    )

    @property
    def tp_lbd_environment(self) -> awslambda.Environment:
        """

        :return:
        """
        if self.environment_vars is NOTHING:
            return self.environment_vars
        elif isinstance(self.environment_vars, dict):
            return awslambda.Environment(
                Variables=self.environment_vars
            )
        elif isinstance(self.environment_vars, awslambda.Environment):
            return self.environment_vars
        else:
            raise TypeError

    def create_aws_resource(self,
                            template,
                            root_module,
                            py_module,
                            py_func=None,
                            py_func_event_class=None):
        pass

    def create_api_resource(self,
                            template,

                            root_module,
                            py_module,
                            py_func=None,
                            py_func_event_class=None
                            ):
        pass


def config_derivable_handler(module_name: str,
                             config_field: str,
                             config_class: typing.Type[LbdFuncConfig],
                             valid_func_name_list: typing.List[str],
                             default_lbd_handler_name: str):
    root_module_name = module_name
    for py_current_module, py_parent_module, py_handler_func in walk_lbd_handler(
            module_name, valid_func_name_list):
        print(py_current_module.__name__)
        rel_module_name = py_current_module.__name__.replace(root_module_name, "")
        if rel_module_name.startswith("."):
            rel_module_name = rel_module_name[1:]


        current_module_config = getattr(py_current_module, config_field)  # type: LbdFuncConfig

        apigw_resource_path_part = slugify(py_current_module.__name__.split(".")[-1])
        if current_module_config.apigw_resource_path_part is NOTHING:
            current_module_config.apigw_resource_path_part = apigw_resource_path_part

        if py_handler_func is not None:
            py_handler_func_config = py_handler_func.__dict__.get(
                config_field, config_class()
            )  # type: LbdFuncConfig
            if py_handler_func_config.apigw_resource_path_part is NOTHING:
                py_handler_func_config.apigw_resource_path_part = apigw_resource_path_part

            if py_handler_func.__name__ == default_lbd_handler_name:
                function_name = slugify(rel_module_name.replace(".", "-"))
            else:
                function_name = slugify(rel_module_name.replace(".", "-") + "-" + py_handler_func.__name__)
            if py_handler_func_config.function_name is NOTHING:
                py_handler_func_config.function_name = function_name


            # print(py_handler_func_config)
