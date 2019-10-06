# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx


from lbdrabbit.lbd_func_config.lbd_func_config import LbdFuncConfig



class TestLbdFuncConfig(object):
    pass






if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
