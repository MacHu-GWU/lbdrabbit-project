# -*- coding: utf-8 -*-

import pytest
from lbdrabbit.config_inherit import iterator
from lbdrabbit.const import VALID_LBD_HANDLER_FUNC_NAME_LIST


def test_walk_lbd_handler():
    mapper = dict()
    for current_module, parent_module, lbd_handler_func in iterator.walk_lbd_handler(
            "lbdrabbit.tests.handlers", VALID_LBD_HANDLER_FUNC_NAME_LIST):
        mapper[current_module.__name__] = dict(
            current_module=current_module,
            parent_module=parent_module,
            lbd_handler_func=lbd_handler_func,
        )


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
