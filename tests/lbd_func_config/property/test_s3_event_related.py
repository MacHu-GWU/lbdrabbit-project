# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from importlib import import_module
from lbdrabbit.lbd_func_config.lbd_func_config import (
    LbdFuncConfig, s3,
    Parameter, Ref, GetAtt, Sub
)
from lbdrabbit.lbd_func_config.tests import new_conf_inst


def handler(event, context): pass


class TestLbdFuncConfig(object):
    def test_s3_notification_configuration(self):
        conf = new_conf_inst()
        conf.s3_event_lbd_config_list = [
            LbdFuncConfig.S3EventLambdaConfig(
                event=LbdFuncConfig.S3EventLambdaConfig.EventEnum.created
            )
        ]
        assert isinstance(conf.s3_notification_configuration_aws_property.LambdaConfigurations, list)
        assert len(conf.s3_notification_configuration_aws_property.LambdaConfigurations) == 1
        assert isinstance(conf.s3_notification_configuration_aws_property.LambdaConfigurations[0].Event, str)
        assert isinstance(conf.s3_notification_configuration_aws_property.LambdaConfigurations[0].Function, GetAtt)

    def test_s3_event_bucket(self):
        conf = new_conf_inst()
        conf.param_env_name = Parameter("EnvironmentName", Type="String")
        conf.s3_event_bucket_yes = True
        conf.s3_event_lbd_config_list = [
            LbdFuncConfig.S3EventLambdaConfig(
                event=LbdFuncConfig.S3EventLambdaConfig.EventEnum.created
            )
        ]
        conf.s3_event_bucket_basename = "data-store"
        assert conf.s3_event_bucket_logic_id == "S3BucketDataStore"
        assert isinstance(conf.s3_event_bucket_name_for_cf, Sub)

        conf.s3_event_bucket_aws_object_pre_check()
        assert conf.s3_event_bucket_aws_object_ready() is True
        assert isinstance(conf.s3_event_bucket_aws_object, s3.Bucket)
        # assert isinstance(conf.s3_event_bucket_aws_object, s3.Bucket)

        # doesn't meet requirement
        conf = LbdFuncConfig()
        conf._py_module = import_module(handler.__module__)
        conf._py_function = handler

        with raises(ValueError):
            conf.s3_event_bucket_aws_object_pre_check()
        assert conf.s3_event_bucket_aws_object_ready() is False


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
