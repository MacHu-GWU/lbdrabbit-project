
.. image:: https://readthedocs.org/projects/lbdrabbit/badge/?version=latest
    :target: https://lbdrabbit.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://travis-ci.org/MacHu-GWU/lbdrabbit-project.svg?branch=master
    :target: https://travis-ci.org/MacHu-GWU/lbdrabbit-project?branch=master

.. image:: https://codecov.io/gh/MacHu-GWU/lbdrabbit-project/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/MacHu-GWU/lbdrabbit-project

.. image:: https://img.shields.io/pypi/v/lbdrabbit.svg
    :target: https://pypi.python.org/pypi/lbdrabbit

.. image:: https://img.shields.io/pypi/l/lbdrabbit.svg
    :target: https://pypi.python.org/pypi/lbdrabbit

.. image:: https://img.shields.io/pypi/pyversions/lbdrabbit.svg
    :target: https://pypi.python.org/pypi/lbdrabbit

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/lbdrabbit-project

------


.. image:: https://img.shields.io/badge/Link-Document-blue.svg
      :target: https://lbdrabbit.readthedocs.io/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
      :target: https://lbdrabbit.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
      :target: https://lbdrabbit.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
      :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/lbdrabbit-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
      :target: https://github.com/MacHu-GWU/lbdrabbit-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
      :target: https://github.com/MacHu-GWU/lbdrabbit-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://pypi.org/pypi/lbdrabbit#files


Welcome to ``lbdrabbit`` Documentation
==============================================================================

Documentation for ``lbdrabbit``.


**设计思路**

Lambda Function 是 Serverless Architect 中的核心部件. 而架构中常用的中间件有:

- Api Gateway, 用于向外部提供调用接口.
- SQS, Kinesis Stream, DynamoDB Stream, 通过流中间件触发 Lambda Function
- Event Rule, 根据 Cron Job 的规则, 定时触发 Lambda.
- S3 Put Object Event, 由存储桶中的数据更新的事件触发.

那么我就会开始想, 能不能开发一个框架, 让我们专注于 Lambda Function 的核心处理逻辑实现, 以及事件驱动的规则定义, 然后自动的生成那些与部署相关的代码呢?

在对开源社区进行了一番调查之后发现, 目前已有 Serverless Framework 和 AWS Sam 两个框架. 这两个框架都可以简化 Lambda Function 的部署, 但是需要用户自行维护除 AWS Lambda 以外的模块的部署, 例如 API Gateway, S3, SQS, Kinesis, DynamoDB Stream. 另一个问题是, 他们都使用了 YML 格式的配置文件, 但是当 Lambda Function 数量很多时, 仍然需要手动的一个一个指定每个 Lambda Function 的具体配置.

于是, 我萌生了一个想法, 能不能 Lambda Function 的配置 像 Python 中的 类继承 一样简单和灵活呢? 能不能由 Lambda Function 的配置, 自动推导出其他系统的配置, 并自动帮我们部署这些系统呢?

这就是 lbdrabbit 诞生的原因.


.. _install:

Install
------------------------------------------------------------------------------

``lbdrabbit`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install lbdrabbit

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade lbdrabbit