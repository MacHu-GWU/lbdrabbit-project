# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from importlib import import_module
from lbdrabbit.const import VALID_LBD_HANDLER_FUNC_NAME_LIST, DEFAULT_LBD_HANDLER_FUNC_NAME
from lbdrabbit.config_inherit.base import config_inherit_handler
from lbdrabbit.config_inherit.lbd_func_config import (
    LbdFuncConfig,
    DEFAULT_LBD_FUNC_CONFIG_FIELD,
    lbd_func_config_value_handler,
    REQUIRED, NOTHING,
    Ref, GetAtt, Sub,
    awslambda, apigateway, events,
)


def access_lbd_config(path) -> LbdFuncConfig:
    """
    helper method to access value of a field in LbdFuncConfig
    """
    parts = path.split(".")
    try:
        return getattr(
            import_module(".".join(parts)),
            DEFAULT_LBD_FUNC_CONFIG_FIELD
        )
    except:
        return getattr(
            getattr(
                import_module(".".join(parts[:-1])),
                parts[-1],
            ),
            DEFAULT_LBD_FUNC_CONFIG_FIELD,
        )


def test_lbd_func_config_value_handler():
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

    conf = access_lbd_config("lbdrabbit.example.handlers.rest")
    assert conf.identifier == "lbdrabbit.example.handlers.rest.{}".format(DEFAULT_LBD_FUNC_CONFIG_FIELD)
    assert conf._py_module.__name__ == "lbdrabbit.example.handlers.rest"
    assert conf._py_function is NOTHING
    assert conf.rel_module_name == "rest"
    assert conf.apigw_resource_logic_id == "ApigwResourceRest"
    assert conf.apigw_resource_path_part == "rest"
    # its a top level resource, so ParentId is a GetAtt of a RestApi
    assert isinstance(conf.apigw_resource_parent_id, GetAtt)
    assert isinstance(conf.apigw_resource_aws_object.ParentId, GetAtt)

    conf = access_lbd_config("lbdrabbit.example.handlers.rest.users")
    assert conf._py_module.__name__ == "lbdrabbit.example.handlers.rest.users"
    assert conf._py_function is NOTHING
    assert conf.rel_module_name == "rest.users"
    assert conf.apigw_resource_logic_id == "ApigwResourceRestUsers"
    assert conf.apigw_resource_path_part == "users"
    # not top level resource, so ParentId is a reference
    assert isinstance(conf.apigw_resource_parent_id, Ref)
    assert isinstance(conf.apigw_resource_aws_object.ParentId, Ref)

    # Scheduled Job Event
    conf = access_lbd_config("lbdrabbit.example.handlers.sched.heart_beap.handler")
    assert conf.scheduled_job_expression_list == ["rate(1 minutes)", ]

    assert isinstance(conf.lbd_func_aws_object, awslambda.Function)
    assert isinstance(conf.scheduled_job_event_rule_aws_objects["rate(1 minutes)"], events.Rule)
    assert isinstance(conf.scheduled_job_event_lbd_permission_aws_objects["rate(1 minutes)"], awslambda.Permission)

    conf = access_lbd_config("lbdrabbit.example.handlers.sched.backup_db.handler")
    assert conf.scheduled_job_expression_list == ["cron(15 10 * * ? *)", ]
    assert isinstance(conf.lbd_func_aws_object, awslambda.Function)
    assert isinstance(conf.scheduled_job_event_rule_aws_objects["cron(15 10 * * ? *)"], events.Rule)
    assert isinstance(conf.scheduled_job_event_lbd_permission_aws_objects["cron(15 10 * * ? *)"], awslambda.Permission)

    # apigateway.Authorizer
    conf = access_lbd_config("lbdrabbit.example.handlers.auth.handler")
    assert isinstance(conf.apigw_authorizer_aws_object.RestApiId, Ref)
    assert len(conf.apigw_authorizer_aws_object.DependsOn) == 2

    # apigateway.Method RPC style
    conf = access_lbd_config("lbdrabbit.example.handlers.rpc.add_two.handler")
    print(conf.apigw_method_authorization_type)

    assert conf.apigw_method_aws_object.AuthorizationType == "CUSTOM"
    assert isinstance(conf.apigw_method_aws_object.AuthorizerId, Ref)
    print(conf.apigw_method_aws_object.Integration)

    # assert conf._py_module.__name__ == "lbdrabbit.example.handlers.rest.users"
    # assert conf._py_function is NOTHING
    #
    # assert conf.rel_module_name == "rest.users"
    # assert conf.api_resource_logic_id == "ApigwResourceRestUsers"
    # assert isinstance(conf.api_resource_parent_id, Ref)
    # assert conf.api_resource_path_part == "users"

    # conf = access_lbd_config("lbdrabbit.example.handlers.rest.users.get")
    # assert conf._py_module.__name__ == "lbdrabbit.example.handlers.rest.users"
    # assert conf._py_function.__name__ == "get"

    # print(conf._py_function)
    # assert conf._py_function.__name__ == "lbdrabbit.example.handlers.rest.users"

    # print("===")
    # print(conf._py_module.__name__, conf._py_function.__module__, "asdfasdf")


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
