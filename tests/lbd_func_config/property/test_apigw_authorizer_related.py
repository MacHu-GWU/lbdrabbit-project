# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from lbdrabbit.lbd_func_config.lbd_func_config import (
    LbdFuncConfig, NOTHING,
    Ref
)
from lbdrabbit.lbd_func_config.tests import new_conf_inst


class TestLbdFunctionConfigApigwAuthorizer(object):
    def test_custom_lambda_authorizer(self):
        conf = new_conf_inst()
        conf.apigw_authorizer_yes = True
        conf.apigw_restapi = "RestApi"
        conf.apigw_authorizer_token_type_header_field = "auth"

        assert conf.apigw_authorizer_aws_object.AuthType == "custom"
        assert conf.apigw_authorizer_aws_object.Type == "TOKEN"
        assert isinstance(conf.apigw_authorizer_aws_object.RestApiId, Ref)
        assert len(conf.apigw_authorizer_aws_object.DependsOn) == 2  # apigateway.RestApi and awslambda.Function
        assert conf.apigw_authorizer_aws_object.IdentitySource == "method.request.header.auth"

        # doesn't meet requirement
        conf = new_conf_inst()
        with raises(ValueError):
            conf.apigw_authorizer_aws_object_pre_check()
        assert conf.apigw_authorizer_aws_object_ready() is False

        conf.apigw_restapi = "RestApi"
        conf.apigw_authorizer_aws_object_pre_check()
        assert conf.apigw_authorizer_aws_object_ready() is False

        conf.apigw_authorizer_yes = True
        conf.apigw_authorizer_aws_object_pre_check()
        assert conf.apigw_authorizer_aws_object_ready() is True

        conf._py_function = NOTHING
        with raises(ValueError):
            conf.apigw_authorizer_aws_object_pre_check()
        assert conf.apigw_authorizer_aws_object_ready() is False


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
