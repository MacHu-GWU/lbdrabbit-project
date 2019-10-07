# -*- coding: utf-8 -*-

import pytest
import inspect
from lbdrabbit.lbd_func_config.lbd_func_config import LbdFuncConfig, DEFAULT_LBD_FUNC_CONFIG_FIELD


def handler(event, context): pass


def test_lbd_func_config_identifier():
    conf = LbdFuncConfig()
    conf._py_module = inspect.getmodule(conf)
    conf._py_function = handler
    assert conf.identifier == "{}.handler.{}".format(
        LbdFuncConfig.__module__,
        DEFAULT_LBD_FUNC_CONFIG_FIELD,
    )


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
