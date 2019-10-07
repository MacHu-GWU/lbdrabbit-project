# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from importlib import import_module
from lbdrabbit.const import VALID_LBD_HANDLER_FUNC_NAME_LIST, DEFAULT_LBD_HANDLER_FUNC_NAME
from lbdrabbit.lbd_func_config.base import config_inherit_handler
from lbdrabbit.lbd_func_config.lbd_func_config import (
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


def test_rest():
    conf = access_lbd_config("lbdrabbit.example.handlers.rest")
    assert conf.identifier == "lbdrabbit.example.handlers.rest.__lbd_func_config__"

    with raises(Exception):
        conf.lbd_func_aws_object_pre_check()
    conf.apigw_resource_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_method_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_method_lbd_permission_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_authorizer_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_method_options_for_cors_aws_object_pre_check()
    with raises(Exception):
        conf.scheduled_job_event_rule_aws_objects_pre_check()
    with raises(Exception):
        conf.scheduled_job_event_lbd_permission_aws_objects_pre_check()

    assert conf.identifier == "lbdrabbit.example.handlers.rest.{}".format(DEFAULT_LBD_FUNC_CONFIG_FIELD)
    assert conf._py_module.__name__ == "lbdrabbit.example.handlers.rest"
    assert conf._py_function is NOTHING
    assert conf.rel_module_name == "rest"
    assert conf.apigw_resource_logic_id == "ApigwResourceRest"
    assert conf.apigw_resource_path_part == "rest"
    # its a top level resource, so ParentId is a GetAtt of a RestApi
    assert isinstance(conf.apigw_resource_parent_id, GetAtt)
    assert isinstance(conf.apigw_resource_aws_object.ParentId, GetAtt)


def test_rest_users():
    conf = access_lbd_config("lbdrabbit.example.handlers.rest.users")
    assert conf.identifier == "lbdrabbit.example.handlers.rest.users.__lbd_func_config__"

    with raises(Exception):
        conf.lbd_func_aws_object_pre_check()
    conf.apigw_resource_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_method_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_method_lbd_permission_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_method_options_for_cors_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_authorizer_aws_object_pre_check()
    with raises(Exception):
        conf.scheduled_job_event_rule_aws_objects_pre_check()
    with raises(Exception):
        conf.scheduled_job_event_lbd_permission_aws_objects_pre_check()

    assert conf._py_module.__name__ == "lbdrabbit.example.handlers.rest.users"
    assert conf._py_function is NOTHING
    assert conf.rel_module_name == "rest.users"
    assert conf.apigw_resource_logic_id == "ApigwResourceRestUsers"
    assert conf.apigw_resource_path_part == "users"
    # not top level resource, so ParentId is a reference
    assert isinstance(conf.apigw_resource_parent_id, Ref)
    assert isinstance(conf.apigw_resource_aws_object.ParentId, Ref)


def test_rest_users_get():
    conf = access_lbd_config("lbdrabbit.example.handlers.rest.users.get")
    assert conf.identifier == "lbdrabbit.example.handlers.rest.users.get.__lbd_func_config__"
    assert conf.lbd_func_logic_id == "LbdFuncRestUsersGet"

    conf.lbd_func_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_resource_aws_object_pre_check()
    conf.apigw_method_aws_object_pre_check()
    conf.apigw_method_lbd_permission_aws_object_pre_check()
    conf.apigw_method_options_for_cors_aws_object_pre_check()
    conf.apigw_authorizer_aws_object_pre_check()
    with raises(Exception):
        conf.scheduled_job_event_rule_aws_objects_pre_check()
    with raises(Exception):
        conf.scheduled_job_event_lbd_permission_aws_objects_pre_check()

    assert conf.apigw_method_authorization_type == "CUSTOM"


def test_rpc_add_two():
    conf = access_lbd_config("lbdrabbit.example.handlers.rpc.add_two.handler")
    assert conf.identifier == "lbdrabbit.example.handlers.rpc.add_two.handler.__lbd_func_config__"
    assert conf.lbd_func_logic_id == "LbdFuncRpcAddTwoHandler"

    conf.lbd_func_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_resource_aws_object_pre_check()
    conf.apigw_method_aws_object_pre_check()
    conf.apigw_method_lbd_permission_aws_object_pre_check()
    conf.apigw_method_options_for_cors_aws_object_pre_check()
    conf.apigw_authorizer_aws_object_pre_check()
    with raises(Exception):
        conf.scheduled_job_event_rule_aws_objects_pre_check()
    with raises(Exception):
        conf.scheduled_job_event_lbd_permission_aws_objects_pre_check()

    assert conf.apigw_method_authorization_type == "CUSTOM"
    assert conf.apigw_method_aws_object.Integration.Type == "AWS"
    assert conf.apigw_method_aws_object.Integration.IntegrationHttpMethod == "POST"
    assert conf.apigw_method_options_for_cors_aws_object.HttpMethod == "OPTIONS"

    assert ",auth" in conf.apigw_method_options_for_cors_aws_object \
        .Integration \
        .IntegrationResponses[0] \
        .ResponseParameters["method.response.header.Access-Control-Allow-Headers"]


def test_sched_heart_beap_hanlder():
    # Scheduled Job Event
    conf = access_lbd_config("lbdrabbit.example.handlers.sched.heart_beap.handler")
    assert conf.identifier == "lbdrabbit.example.handlers.sched.heart_beap.handler.__lbd_func_config__"
    assert conf.lbd_func_logic_id == "LbdFuncSchedHeartBeapHandler"

    conf.lbd_func_aws_object_pre_check()
    with raises(Exception):
        conf.apigw_resource_aws_object_pre_check()
    conf.apigw_method_aws_object_pre_check()
    conf.apigw_method_lbd_permission_aws_object_pre_check()
    conf.apigw_authorizer_aws_object_pre_check()
    conf.scheduled_job_event_rule_aws_objects_pre_check()
    conf.scheduled_job_event_lbd_permission_aws_objects_pre_check()

    assert conf.scheduled_job_expression_list == ["rate(1 minute)", ]

    assert isinstance(conf.lbd_func_aws_object, awslambda.Function)
    assert isinstance(conf.scheduled_job_event_rule_aws_objects["rate(1 minute)"], events.Rule)
    assert isinstance(conf.scheduled_job_event_lbd_permission_aws_objects["rate(1 minute)"], awslambda.Permission)


def test_sched_backup_db_handler():
    conf = access_lbd_config("lbdrabbit.example.handlers.sched.backup_db.handler")
    assert conf.identifier == "lbdrabbit.example.handlers.sched.backup_db.handler.__lbd_func_config__"
    assert conf.lbd_func_logic_id == "LbdFuncSchedBackupDbHandler"

    assert conf.scheduled_job_expression_list == ["cron(15 10 * * ? *)", ]
    assert isinstance(conf.lbd_func_aws_object, awslambda.Function)
    assert isinstance(conf.scheduled_job_event_rule_aws_objects["cron(15 10 * * ? *)"], events.Rule)
    assert isinstance(conf.scheduled_job_event_lbd_permission_aws_objects["cron(15 10 * * ? *)"], awslambda.Permission)


def test_view_index_handler():
    conf = access_lbd_config("lbdrabbit.example.handlers.view.index.handler")


def test_auth_handler():
    # apigateway.Authorizer
    conf = access_lbd_config("lbdrabbit.example.handlers.auth.handler")
    assert conf.identifier == "lbdrabbit.example.handlers.auth.handler.__lbd_func_config__"
    assert conf.lbd_func_logic_id == "LbdFuncAuthHandler"

    assert isinstance(conf.apigw_authorizer_aws_object.RestApiId, Ref)
    assert len(conf.apigw_authorizer_aws_object.DependsOn) == 2
    assert conf.apigw_authorizer_aws_object.IdentitySource == "method.request.header.auth"

    # apigateway.Method RPC style
    conf = access_lbd_config("lbdrabbit.example.handlers.rpc.add_two.handler")

    assert conf.apigw_method_aws_object.AuthorizationType == "CUSTOM"
    assert isinstance(conf.apigw_method_aws_object.AuthorizerId, Ref)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
