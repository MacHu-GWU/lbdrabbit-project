# -*- coding: utf-8 -*-

from lbdrabbit.config_inherit import LbdFuncConfig, ApiMethodIntType

__lbd_func_config__ = LbdFuncConfig()
__lbd_func_config__.memory = 128
__lbd_func_config__.timeout = 30
__lbd_func_config__.apigw_method_int_type = ApiMethodIntType.rest
