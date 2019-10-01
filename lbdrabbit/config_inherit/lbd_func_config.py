# -*- coding: utf-8 -*-

import typing
import attr
from troposphere_mate import Template, Parameter, Tags, Ref, GetAtt, Sub
from troposphere_mate import awslambda, apigateway

from .base import BaseConfig, REQUIRED, NOTHING


@attr.s
class LbdFuncConfig(object):
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

    _module_name = attr.ib(default=NOTHING)

    _default = dict(
        memory_size=128,
        timeout=3,
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
