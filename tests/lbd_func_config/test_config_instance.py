# -*- coding: utf-8 -*-

import pytest
import attr
from lbdrabbit.lbd_func_config.tests import __lbd_func_config__


def test_evolve():
    conf = attr.evolve(__lbd_func_config__)
    conf.apigw_restapi = "restapi"
    assert conf.apigw_restapi == "restapi"
    assert __lbd_func_config__.apigw_restapi != "restapi"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
