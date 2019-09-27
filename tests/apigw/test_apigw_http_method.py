# -*- coding: utf-8 -*-

import pytest
from lbdrabbit.apigw.http_method import HttpMethod


class TestHttpMethod(object):
    def test(self):
        assert HttpMethod.is_valid_func_name("get") is True
        assert HttpMethod.is_valid_func_name("post") is True
        assert HttpMethod.is_valid_func_name("put") is True
        assert HttpMethod.is_valid_func_name("patch") is True
        assert HttpMethod.is_valid_func_name("delete") is True
        assert HttpMethod.is_valid_func_name("head") is True
        assert HttpMethod.is_valid_func_name("options") is True
        assert HttpMethod.is_valid_func_name("any_") is True

        assert isinstance(HttpMethod.get_all_valid_func_name(), list)
        assert isinstance(HttpMethod.get_all_valid_http_method(), list)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
