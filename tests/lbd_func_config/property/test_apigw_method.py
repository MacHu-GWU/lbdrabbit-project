# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from lbdrabbit.lbd_func_config.lbd_func_config import (
    LbdFuncConfig,
    Parameter,
    Ref, GetAtt, ImportValue,
    apigateway,
)


class TestLbdFunctionConfigApigwMethodAuthorizer(object):
    def test_apigw_method_use_authorizer_yes(self):
        conf = LbdFuncConfig()
        assert conf.apigw_method_use_authorizer_yes is False

        conf = LbdFuncConfig(
            apigw_method_authorization_type=LbdFuncConfig.ApigwMethodAuthorizationType.none,
        )
        assert conf.apigw_method_use_authorizer_yes is False

        conf = LbdFuncConfig(
            apigw_method_authorization_type=LbdFuncConfig.ApigwMethodAuthorizationType.custom,
        )
        assert conf.apigw_method_use_authorizer_yes is True

        conf = LbdFuncConfig(
            apigw_method_authorization_type=LbdFuncConfig.ApigwMethodAuthorizationType.cognito_user_pools,
        )
        assert conf.apigw_method_use_authorizer_yes is True

        conf = LbdFuncConfig(
            apigw_method_authorization_type=LbdFuncConfig.ApigwMethodAuthorizationType.aws_iam,
        )
        assert conf.apigw_method_use_authorizer_yes is True

    def test_apigw_method_authorizer_id_for_cf(self):
        conf = LbdFuncConfig(
            apigw_method_authorizer=apigateway.Authorizer(
                "ApigwAuthorizer",
                Name="",
                Type="",
                AuthorizerUri="",
                IdentitySource="",
            ),
        )
        assert isinstance(conf.apigw_method_authorizer_id_for_cf, Ref)

        conf = LbdFuncConfig(
            apigw_method_authorizer=Ref("ApigwAuthorizer"),
        )
        assert isinstance(conf.apigw_method_authorizer_id_for_cf, Ref)

        conf = LbdFuncConfig(
            apigw_method_authorizer=GetAtt("NestedStack1", "AuthorizerId"),
        )
        assert isinstance(conf.apigw_method_authorizer_id_for_cf, GetAtt)

        conf = LbdFuncConfig(
            apigw_method_authorizer=ImportValue("authorizer-id-export-name"),
        )
        assert isinstance(conf.apigw_method_authorizer_id_for_cf, ImportValue)

        conf = LbdFuncConfig(
            apigw_method_authorizer=Parameter(
                "ApigwAuthorizerId",
                Type="String",
            ),
        )
        assert isinstance(conf.apigw_method_authorizer_id_for_cf, Ref)

        conf = LbdFuncConfig(
            apigw_method_authorizer=Ref("ApigwAuthorizer"),
        )
        assert isinstance(conf.apigw_method_authorizer_id_for_cf, Ref)

        conf = LbdFuncConfig(
            apigw_method_authorizer="ApigwAuthorizer",
        )
        assert conf.apigw_method_authorizer_id_for_cf == "ApigwAuthorizer"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
