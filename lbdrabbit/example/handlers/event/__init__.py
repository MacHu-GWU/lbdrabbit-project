# -*- coding: utf-8 -*-

from lbdrabbit import LbdFuncConfig


__lbd_func_config__ = LbdFuncConfig()
__lbd_func_config__.s3_lbd_config_list = [
    LbdFuncConfig.S3EventLambdaConfig(
        event=LbdFuncConfig.S3EventLambdaConfig.EventEnum.created,
    )
]

