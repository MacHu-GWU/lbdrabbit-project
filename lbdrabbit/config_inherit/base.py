# -*- coding: utf-8 -*-

import attr
from troposphere_mate.core.sentiel import Sentinel, NOTHING, REQUIRED


@attr.s
class BaseConfig(object):
    """
    Lambda Function Level Config.

    Every child function under a resource inherits :class:`ResourceConfig``.

    **中文文档**

    一个特殊的用于指定配置的数据类型. 该基础类用于指定 Lambda Function, API Gateway Method
    等配置.

    - 所有必要的属性都给予 ``REQUIRED`` 默认值
    - 所有可选的属性都给予 ``NOTHING`` 默认值
    """
    _default = dict()  # type: dict

    def absorb(self, other):
        """
        inherit values from other config if the current one is a Sentinel.

        :type other: FunctionConfig

        **中文文档**

        从另一个 实例 当中吸取那些被数值化的数据.
        """
        this_data = attr.asdict(self)
        other_data = attr.asdict(other)
        for key, value in this_data.items():
            if isinstance(value, Sentinel):
                if key in other_data:
                    setattr(self, key, other_data[key])

    def fill_na_with_default(self):
        """
        Fill default value into current instance, if the field already has
        a value, then skip that field.

        **中文文档**

        针对于可选属性, 如果用户未指定初始值, 则使用 ``_default`` 变量中的值.
        """
        for key, value in self._default.items():
            if isinstance(getattr(self, key), Sentinel):
                setattr(self, key, value)

    def post_init_hooker(self):
        """
        """
        pass