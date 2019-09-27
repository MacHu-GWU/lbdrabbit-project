# -*- coding: utf-8 -*-

"""
**中文文档**

此模块的作用是使得 :class:`~lbdrabbit.config_inherit.base.BaseConfig`` 实例能够以
package -> module -> function 的顺序 继承设定值.

举例来说, 我们自定义了一个 ``LbdFuncConfig``类, 并将其指定给 lambda handler 函数的
__func_config__ 属性. 其中有一个设定值叫 timeout.

然后对于一个 handler 函数, 我们定义了 ``LbdFuncConfig``, 但没有指定 timeout.

1. 那么我们会去 module 级别寻找 __func_config__ 属性, 如果在 module 级压根没有被定义,
那么去更上一层的 package 中的 __func_config__ 属性寻找, 直到找到为止.
2. 如果直到最顶层的 package 中都没有找到, 那么最后检查这个值, 如果是 REQUIRED, 就报错.

如果我们指定了 timeout, 那么以我们的指定值为准, 忽略上层 module 中的定义值.
"""

import typing
from importlib import import_module
from picage import Package
from .base import BaseConfig


def inherit_handler(module_name: str,
                    config_field: str,
                    config_class: typing.Type[BaseConfig],
                    valid_func_name_list: typing.List[str],
                    _parent_config: BaseConfig = None):
    """

    :param module_name:
    :param config_field:
    :param config_class:
    :param valid_func_name_list:

    :param _parent_config:

    :return:


    **中文文档**

    /handlers
    /handlers/orm
    /handlers/orm/users.py

    """
    if _parent_config is None:
        _parent_config = config_class()

    current_pkg = Package(module_name)
    sub_packages = list(current_pkg.sub_packages.values())
    sub_modules = list(current_pkg.sub_modules.values())

    py_module = import_module(current_pkg.fullname)

    module_config = py_module.__dict__.get(
        config_field, config_class()
    )  # type: BaseConfig
    module_config.absorb(_parent_config)
    setattr(py_module, config_field, module_config)

    for http_method in valid_func_name_list:
        if http_method in py_module.__dict__:
            py_handler_func = getattr(py_module, http_method)

            func_config = py_handler_func.__dict__.get(
                config_field, config_class()
            )  # type: BaseConfig
            func_config.absorb(module_config)
            setattr(py_handler_func, config_field, func_config)

    for sub_pkg in (sub_packages + sub_modules):
        inherit_handler(
            module_name=sub_pkg.fullname,
            config_field=config_field,
            config_class=config_class,
            valid_func_name_list=valid_func_name_list,
            _parent_config=module_config,
        )
