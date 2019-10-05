# -*- coding: utf-8 -*-

import typing
import attr
import string
from importlib import import_module
from picage import Package
from troposphere_mate import Template, Parameter, Tags, Ref, GetAtt, Sub
from troposphere_mate import awslambda, apigateway, iam, events
from troposphere_mate import slugify, camelcase, helper_fn_sub

from .base import BaseConfig, REQUIRED, NOTHING, walk_lbd_handler
from ..pkg.fingerprint import fingerprint

DEFAULT_LBD_FUNC_CONFIG_FIELD = "__lbd_func_config__"


class ApiMethodIntType:
    rest = "rest"
    rpc = "rpc"
    html = "html"

    _valid_values = set()


for k, v in ApiMethodIntType.__dict__.items():
    if not k.startswith("_"):
        ApiMethodIntType._valid_values.add(v)


@attr.s
class LbdFuncConfig(BaseConfig):
    """
    Lambda Function Level Config.

    Every child function under a resource inherits :class:`ResourceConfig``.


    :param apigw_authorizer_yes: indicate if this lambda function is used
        as a custom authorizer.

    **中文文档**



    **设计**

    - something_aws_object: 以 aws_object 结尾的 property 方法, 返回的是一个具体的
        ``troposphere_mate.AWSObject`` 对象
    - pre_exam
    - create_something: 以 create 开头的方法会调用响应的 something_aws_object
        方法, 不过在那之前,

    """
    param_env_name = attr.ib(default=REQUIRED)  # type: Parameter

    lbd_func_yes = attr.ib(default=REQUIRED)  # type: str
    lbd_func_name = attr.ib(default=REQUIRED)  # type: str
    lbd_func_description = attr.ib(default=NOTHING)  # type: str
    lbd_func_memory_size = attr.ib(default=NOTHING)  # type: int
    lbd_func_iam_role = attr.ib(default=REQUIRED)  # type: typing.Union[iam.Role, Ref, GetAtt, Parameter, str]
    lbd_func_timeout = attr.ib(default=NOTHING)  # type: int
    lbd_func_runtime = attr.ib(default=REQUIRED)  # type: str
    lbd_func_code = attr.ib(default=REQUIRED)  # type: awslambda.Code
    lbd_func_layers = attr.ib(default=NOTHING)  # type: list
    lbd_func_reserved_concurrency = attr.ib(default=NOTHING)  # type: int
    lbd_func_environment_vars = attr.ib(default=NOTHING)  # type: awslambda.Environment
    lbd_func_kms_key_arn = attr.ib(default=NOTHING)  # type: str
    lbd_func_vpc_config = attr.ib(default=NOTHING)  # type: awslambda.VPCConfig
    lbd_func_dead_letter_config = attr.ib(default=NOTHING)  # type: awslambda.DeadLetterConfig
    lbd_func_tracing_config = attr.ib(default=NOTHING)  # type: awslambda.TracingConfig

    _lbd_func_aws_object_cache = attr.ib(default=NOTHING)  # type: awslambda.Function

    lbd_func_metadata = attr.ib(default=NOTHING)  # type: dict
    lbd_func_tags = attr.ib(default=NOTHING)  # type: Tags

    apigw_resource_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_restapi = attr.ib(default=NOTHING)  # type: apigateway.RestApi
    _apigw_resource_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Resource

    apigw_method_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_method_int_type = attr.ib(default=NOTHING)  # type: str
    _apigw_method_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Method
    _apigw_method_lbd_permission_aws_object_cache = attr.ib(default=NOTHING)  # type: awslambda.Permission

    apigw_method_int_passthrough_behavior = attr.ib(default=NOTHING)  # type: str
    apigw_method_int_timeout_in_milli = attr.ib(default=NOTHING)  # type: int
    apigw_method_authorization_type = attr.ib(default=NOTHING)  # type: str
    apigw_method_authorizer = attr.ib(default=NOTHING)  # type: apigateway.Authorizer

    apigw_method_enable_cors_yes = attr.ib(default=NOTHING)  # type: str
    apigw_method_enable_cors_access_control_allow_origin = attr.ib(default=NOTHING)  # type: str
    apigw_method_enable_cors_access_control_allow_headers = attr.ib(default=NOTHING)  # type: str
    _apigw_method_options_for_cors_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Method

    apigw_authorizer_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_authorizer_name = attr.ib(default=NOTHING)  # type: bool
    apigw_authorizer_token_type_header_field = attr.ib(default=NOTHING)  # type: bool

    _apigw_authorizer_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Authorizer
    _apigw_authorizer_lbd_permission_aws_object_cache = attr.ib(default=NOTHING)  # type: awslambda.Permission

    scheduled_job_yes = attr.ib(default=NOTHING)  # type: bool
    scheduled_job_expression = attr.ib(default=NOTHING)  # type: typing.Union[str, typing.List[str]]
    _scheduled_job_event_rule_aws_objects_cache = attr.ib(default=NOTHING)  # type: typing.Dict[str, events.Rule]
    _scheduled_job_event_lbd_permission_aws_objects_cache = attr.ib(
        default=NOTHING)  # type: typing.Dict[str, awslambda.Permission]

    _root_module_name = attr.ib(default=NOTHING)
    _py_module = attr.ib(default=NOTHING)
    _py_function = attr.ib(default=NOTHING)
    _py_parent_module = attr.ib(default=NOTHING)

    _default = dict(
        lbd_func_yes=True,
        memory_size=128,
        timeout=3,
        apigw_resource_yes=False,
        apigw_method_yes=False,
        apigw_method_int_passthrough_behavior="WHEN_NO_MATCH",
        apigw_method_int_timeout_in_milli=29000,
        apigw_authorizer_yes=False,
        apigw_authorizer_token_type_header_field="auth",
    )

    @property
    def identifier(self) -> str:
        try:
            return "{}.{}.{}".format(
                self._py_module.__name__, self._py_function.__name__, DEFAULT_LBD_FUNC_CONFIG_FIELD
            )
        except:
            return "{}.{}".format(
                self._py_module.__name__, DEFAULT_LBD_FUNC_CONFIG_FIELD
            )

    @property
    def parent_config(self) -> 'LbdFuncConfig':
        """
        Access the parent lambda function config.
        """
        # it is a module level config
        if self._py_function is NOTHING:
            return getattr(self._py_parent_module, DEFAULT_LBD_FUNC_CONFIG_FIELD)
        # it is a function level config
        else:
            return getattr(self._py_parent_module, DEFAULT_LBD_FUNC_CONFIG_FIELD)

    @property
    def rel_module_name(self) -> str:
        """
        Relative module name, compared to the root module

        For example, if the root module is ``"a.b"``, and this module is ``"a.b.c.d"``,
        then the relative module name is ``"c.d"``; if this module is ``"a.b"``,
        then the relative module name is ``""``
        """
        rel_module_name = self._py_module.__name__.replace(self._root_module_name, "")
        if rel_module_name.startswith("."):
            rel_module_name = rel_module_name[1:]
        return rel_module_name

    def is_module(self):
        if self._py_function is NOTHING:
            return True
        else:
            return False

    def is_function(self):
        if self._py_function is NOTHING:
            return False
        else:
            return True

    @property
    def lbd_func_logic_id(self) -> str:
        return "LbdFunc{}".format(
            camelcase(self.rel_module_name.replace(".", "-")) + camelcase(self._py_function.__name__)
        )

    @property
    def lbd_func_iam_role_arn(self):
        if isinstance(self.lbd_func_iam_role, iam.Role):  # a troposphere_mate IAM Role object
            return GetAtt(self.lbd_func_iam_role, "Arn")
        elif isinstance(self.lbd_func_iam_role,
                        (Ref, GetAtt)):  # reference of a parameter or get attribute instrinct function
            return self.lbd_func_iam_role
        elif isinstance(self.lbd_func_iam_role, Parameter):  # a parameter represent a iam role ARN
            return Ref(self.lbd_func_iam_role)
        elif isinstance(self.lbd_func_iam_role, str):  # an ARN string
            return self.lbd_func_iam_role
        else:
            raise TypeError(
                "{}.lbd_func_iam_role has to be one of "
                "troposphere_mate.iam.Role, "
                "Ref of a Parameter, "
                "GetAtt of a troposphere_mate.iam.Role, "
                "a Parameter represent a iam role ARN, "
                "a string represent a iam role ARN".format(self.identifier))

    def lbd_func_aws_object_pre_check(self):
        if callable(self._py_function):
            try:
                self._py_function.__name__
            except AttributeError:
                raise TypeError("{}.{} is not a valid function".format(self._py_module.__name__, self._py_function))
        else:
            raise TypeError("{}.{} is not a valid function".format(self._py_module.__name__, self._py_function))

    @property
    def lbd_func_aws_object(self) -> awslambda.Function:
        if self.lbd_func_yes is not True:
            return self._lbd_func_aws_object_cache

        if self._lbd_func_aws_object_cache is NOTHING:
            lbd_func = awslambda.Function(
                self.lbd_func_logic_id,
                FunctionName=helper_fn_sub("{}-%s" % self.lbd_func_name, self.param_env_name),
                Handler="{}.{}".format(self._py_module.__name__, self._py_function.__name__),
                Code=self.lbd_func_code,
                Role=self.lbd_func_iam_role_arn,
                Runtime=self.lbd_func_runtime,
            )
            if self.lbd_func_memory_size is not NOTHING:
                lbd_func.MemorySize = self.lbd_func_memory_size
            if self.lbd_func_timeout is not NOTHING:
                lbd_func.Timeout = self.lbd_func_timeout
            if self.lbd_func_layers is not NOTHING:
                lbd_func.Layers = self.lbd_func_layers
            if self.lbd_func_reserved_concurrency is not NOTHING:
                lbd_func.ReservedConcurrentExecutions = self.lbd_func_reserved_concurrency
            if self.lbd_func_environment_vars is not NOTHING:
                lbd_func.Environment = self.lbd_func_environment_vars
            if self.lbd_func_kms_key_arn is not NOTHING:
                lbd_func.KmsKeyArn = self.lbd_func_kms_key_arn
            if self.lbd_func_vpc_config is not NOTHING:
                lbd_func.VpcConfig = self.lbd_func_vpc_config
            if self.lbd_func_dead_letter_config is not NOTHING:
                lbd_func.DeadLetterConfig = self.lbd_func_dead_letter_config
            if self.lbd_func_tracing_config is not NOTHING:
                lbd_func.TracingConfig = self.lbd_func_tracing_config

            self._lbd_func_aws_object_cache = lbd_func

        return self._lbd_func_aws_object_cache

    @property
    def apigw_resource_logic_id(self) -> str:
        """
        Api Gateway Resource Logic Id is Full Resource Path in Camelcase format
        with a Prefix.
        """
        return "ApigwResource{}".format(
            camelcase(self.rel_module_name.replace(".", "-")))

    @property
    def apigw_resource_parent_id(self) -> typing.Union[Ref, GetAtt]:
        # it is the root module, use RootResourceId as parent id
        if ("." not in self.rel_module_name) and bool(self.rel_module_name):
            return GetAtt(self.apigw_restapi, "RootResourceId")
        else:
            return Ref(self.parent_config.apigw_resource_aws_object)

    @property
    def apigw_resource_path_part(self) -> str:
        """
        The file name (without .py extension) of current module becomes
        api gateway resource.
        """
        return slugify(self._py_module.__name__.split(".")[-1])

    @property
    def apigw_resource_full_path(self) -> str:
        """
        if current_module = lbdrabbit.examples.handlers.rest.users.py,
        root_module = lbdrabbit.examples.handlers

        then the api gateway resource full path should be
        ``rest/users``
        """
        return "/".join([
            slugify(fname)
            for fname in self.rel_module_name.split(".")
        ])

    def apigw_resource_aws_object_pre_check(self):
        """

        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.apigateway.Resource 的条件

        - LbdFuncConfig._py_function 必须为 None, 因为如果当前绑定了一个函数,
            说明我们需要的是 Api Method 而不是 Api Resource
        - LbdFuncConfig.apigw_restapi 必须被指定.
        """
        if self._py_function is not NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "the config should not bound with a python function!")

        if self.apigw_restapi is NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "LbdFuncConfig.apigw_restapi has to be specified")

    @property
    def apigw_resource_aws_object(self) -> apigateway.Resource:
        if self.apigw_resource_yes is not True:
            return self._apigw_resource_aws_object_cache

        if self._apigw_resource_aws_object_cache is NOTHING:
            apigw_resource = apigateway.Resource(
                self.apigw_resource_logic_id,
                RestApiId=Ref(self.apigw_restapi),
                ParentId=self.apigw_resource_parent_id,
                PathPart=self.apigw_resource_path_part,
                DependsOn=[self.apigw_restapi],
            )
            self._apigw_resource_aws_object_cache = apigw_resource
        return self._apigw_resource_aws_object_cache

    @property
    def apigw_method_logic_id(self) -> str:
        return "ApigwMethod{}".format(
            camelcase(self.rel_module_name.replace(".", "-")) + camelcase(self._py_function.__name__)
        )

    def check_apigw_method_authorization_type(self):
        allowed_values = ["NONE", "AWS_IAM", "CUSTOM", "COGNITO_USER_POOLS"]
        if self.apigw_method_authorization_type.upper() not in allowed_values:
            raise ValueError(
                "{}.apigw_method_authorization_type can only be one of {}". \
                    format(self.identifier, allowed_values)
            )

    def check_apigw_method_int_type(self):
        if self.apigw_method_int_type not in ApiMethodIntType._valid_values:
            raise ValueError(
                "{}.apigw_method_int_type can only be one of {}". \
                    format(self.identifier, ApiMethodIntType._valid_values)
            )

    @property
    def apigw_method_http_method(self):
        if self.apigw_method_int_type == ApiMethodIntType.rest:
            return self._py_function.__name__.upper()
        elif self.apigw_method_int_type == ApiMethodIntType.rpc:
            return "POST"
        else:
            return "POST"

    def apigw_method_aws_object_pre_check(self):
        """
        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.apigateway.Method 的条件

        - LbdFuncConfig._py_function 必须为Python函数, 不然没有LambdaFunction支持,
            Api Method 就无法工作.
        - LbdFuncConfig.apigw_restapi 必须被指定.
        """
        if self._py_function is NOTHING:
            raise ValueError("to create a apigateway.Method, "
                             "the config must be bound with a python function!")

        if self.apigw_restapi is NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "LbdFuncConfig.apigw_restapi has to be specified")

    @property
    def apigw_method_aws_object(self) -> apigateway.Method:
        if self.apigw_method_yes is not True:
            return self._apigw_method_aws_object_cache

        if self._apigw_method_aws_object_cache is NOTHING:
            depends_on = [
                self.apigw_resource_aws_object,
                self.lbd_func_aws_object,
            ]

            integration = apigateway.Integration(
                Type="AWS",
                IntegrationHttpMethod="POST",
                Uri=Sub(
                    "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${LambdaArn}/invocations",
                    {
                        "Region": {"Ref": "AWS::Region"},
                        "LambdaArn": GetAtt(self.lbd_func_aws_object, "Arn"),
                    }
                ),
                IntegrationResponses=[
                    apigateway.IntegrationResponse(
                        StatusCode="200",
                        ContentHandling="CONVERT_TO_TEXT",
                        ResponseTemplates={"application/json": ""}
                    )
                ],
                RequestTemplates={"application/json": "$input.json('$')"},
            )

            if self.apigw_method_int_passthrough_behavior is not NOTHING:
                integration.PassthroughBehavior = self.apigw_method_int_passthrough_behavior
            if self.apigw_method_int_timeout_in_milli is not NOTHING:
                integration.TimeoutInMillis = self.apigw_method_int_timeout_in_milli

            method_responses = [
                apigateway.MethodResponse(
                    StatusCode="200",
                    ResponseModels={"application/json": "Empty"},
                )
            ]

            if self.apigw_method_enable_cors_yes is True:
                for integration_response in integration.IntegrationResponses:
                    try:
                        integration_response.ResponseParameters[
                            "method.response.header.Access-Control-Allow-Origin"] = "'*'"
                    except:
                        integration_response.ResponseParameters = {
                            "method.response.header.Access-Control-Allow-Origin": "'*'",
                        }

                for method_response in method_responses:
                    try:
                        method_response.ResponseParameters["method.response.header.Access-Control-Allow-Origin"] = False
                    except:
                        method_response.ResponseParameters = {
                            "method.response.header.Access-Control-Allow-Origin": False,
                        }

            self.check_apigw_method_authorization_type()
            self.check_apigw_method_int_type()

            apigw_method = apigateway.Method(
                title=self.apigw_method_logic_id,
                RestApiId=Ref(self.apigw_restapi),
                ResourceId=Ref(self.apigw_resource_aws_object),
                AuthorizationType=self.apigw_method_authorization_type,
                HttpMethod=self.apigw_method_http_method,
                MethodResponses=method_responses,
                Integration=integration,
            )

            if self.apigw_method_authorizer is not NOTHING:
                apigw_method.AuthorizerId = Ref(self.apigw_method_authorizer)
                depends_on.append(self.apigw_method_authorizer)

            apigw_method.DependsOn = depends_on

            self._apigw_method_aws_object_cache = apigw_method
        return self._apigw_method_aws_object_cache

    def apigw_method_lbd_permission_aws_object_pre_check(self):
        self.apigw_method_aws_object_pre_check()
        self.lbd_func_aws_object_pre_check()

    @property
    def apigw_method_lbd_permission_aws_object(self) -> awslambda.Permission:
        if self.apigw_method_yes is not True:
            return self._apigw_method_lbd_permission_aws_object_cache

        if self._apigw_method_lbd_permission_aws_object_cache is NOTHING:
            apigw_method_lbd_permission_logic_id = "LbdPermission{}".format(self.apigw_method_logic_id)
            apigw_method_lbd_permission = awslambda.Permission(
                title=apigw_method_lbd_permission_logic_id,
                Action="lambda:InvokeFunction",
                FunctionName=GetAtt(self.lbd_func_aws_object, "Arn"),
                Principal="apigateway.amazonaws.com",
                SourceArn=Sub(
                    "arn:aws:execute-api:${Region}:${AccountId}:${RestApiId}/*/%s/%s" % \
                    (
                        self.apigw_method_http_method,
                        self.apigw_resource_full_path
                    ),
                    {
                        "Region": {"Ref": "AWS::Region"},
                        "AccountId": {"Ref": "AWS::AccountId"},
                        "RestApiId": Ref(self.apigw_restapi),
                    }
                ),
                DependsOn=[
                    self.apigw_method_aws_object,
                    self.lbd_func_aws_object,
                ]
            )
            self._apigw_method_lbd_permission_aws_object_cache = apigw_method_lbd_permission
        return self._apigw_method_lbd_permission_aws_object_cache

    def apigw_method_options_for_cors_aws_object_pre_check(self):
        self.apigw_method_aws_object_pre_check()

    @property
    def apigw_method_options_for_cors_aws_object(self) -> apigateway.Method:
        """

        **中文文档**

        为了开启 Cors, 对于 Api Resource 是需要一个 Options Method 专门用于获取
        服务器的设置. 这事因为浏览器在检查到跨站请求时, 会使用 Options 方法获取服务器的
        跨站访问设置, 如果不满则, 浏览爱则会返回错误信息.
        """
        if self.apigw_method_enable_cors_yes is not True:
            return self._apigw_method_options_for_cors_aws_object_cache

        # For cors, options method doesn't need a lambda function
        depends_on = [
            self.apigw_resource_aws_object,
        ]

        access_control_allow_headers = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
        if self.apigw_method_authorizer is not NOTHING:
            if self.apigw_authorizer_token_type_header_field is not NOTHING:
                access_control_allow_headers = access_control_allow_headers \
                                               + ",{}".format(self.apigw_authorizer_token_type_header_field)

        integration = apigateway.Integration(
            Type="MOCK",
            IntegrationResponses=[
                apigateway.IntegrationResponse(
                    StatusCode="200",
                    ContentHandling="CONVERT_TO_TEXT",
                    ResponseParameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'",
                        "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,POST'",
                        "method.response.header.Access-Control-Allow-Headers": "'{}'".format(
                            access_control_allow_headers),
                    },
                    ResponseTemplates={"application/json": ""}
                )
            ],
            PassthroughBehavior="WHEN_NO_MATCH",
        )
        if self.apigw_method_int_passthrough_behavior is not NOTHING:
            integration.PassthroughBehavior = self.apigw_method_int_passthrough_behavior
        if self.apigw_method_int_timeout_in_milli is not NOTHING:
            integration.TimeoutInMillis = self.apigw_method_int_timeout_in_milli

        method_responses = [
            apigateway.MethodResponse(
                StatusCode="200",
                ResponseModels={"application/json": "Empty"},
                ResponseParameters={
                    "method.response.header.Access-Control-Allow-Origin": False,
                    "method.response.header.Access-Control-Allow-Methods": False,
                    "method.response.header.Access-Control-Allow-Headers": False,
                }
            )
        ]

        self.check_apigw_method_authorization_type()
        self.check_apigw_method_int_type()

        apigw_method = apigateway.Method(
            title="ApigwMethod{}Options".format(
                camelcase(self.rel_module_name.replace(".", "-"))
            ),
            RestApiId=Ref(self.apigw_restapi),
            ResourceId=Ref(self.apigw_resource_aws_object),
            AuthorizationType="NONE",
            HttpMethod="OPTIONS",
            MethodResponses=method_responses,
            Integration=integration,
        )

        apigw_method.DependsOn = depends_on

        return apigw_method

    # apigateway.Authorizer
    @classmethod
    def get_authorizer_id(cls, rel_module_name):
        return "ApigwAuthorizer{}".format(
            camelcase(rel_module_name.replace(".", "-"))
        )

    @property
    def apigw_authorizer_logic_id(self) -> str:
        return self.get_authorizer_id(self.rel_module_name)

    def apigw_authorizer_aws_object_pre_check(self):
        """
        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.apigateway.Authorizer 的条件

        目前只支持 CUSTOM 的 Lambda Authorizer

        - LbdFuncConfig._py_function 必须为Python函数, 不然没有LambdaFunction支持,
            Api Authorizer 就无法工作.
        - LbdFuncConfig.apigw_restapi 必须被指定.
        """
        if self._py_function is NOTHING:
            raise ValueError("to create a apigateway.Authorizer, "
                             "the config must be bound with a python function!")

        if self.apigw_restapi is NOTHING:
            raise ValueError("to create a apigateway.Resource, "
                             "LbdFuncConfig.apigw_restapi has to be specified")

    @property
    def apigw_authorizer_aws_object(self) -> apigateway.Authorizer:
        if self.apigw_authorizer_yes is not True:
            return self._apigw_authorizer_aws_object_cache

        if self._apigw_authorizer_aws_object_cache is NOTHING:
            if self.apigw_authorizer_name is NOTHING:
                apigw_authorizer_name = self.apigw_authorizer_logic_id
            else:
                apigw_authorizer_name = self.apigw_authorizer_name

            if len(set(apigw_authorizer_name).difference(set(string.ascii_letters + string.digits))):
                raise ValueError(
                    "{}.apigw_authorizer_name can only have letter and digits".format(
                        self.identifier
                    )
                )
            apigw_authorizer = apigateway.Authorizer(
                title=self.apigw_authorizer_logic_id,
                Name=apigw_authorizer_name,
                RestApiId=Ref(self.apigw_restapi),
                AuthType="custom",
                Type="TOKEN",
                IdentitySource="method.request.header.{}".format(self.apigw_authorizer_token_type_header_field),
                AuthorizerResultTtlInSeconds=300,
                AuthorizerUri=Sub(
                    "arn:aws:apigateway:${Region}:lambda:path/2015-03-31/functions/${AuthorizerFunctionArn}/invocations",
                    {
                        "Region": {"Ref": "AWS::Region"},
                        "AuthorizerFunctionArn": GetAtt(self.lbd_func_aws_object, "Arn"),
                    }
                ),
                DependsOn=[
                    self.lbd_func_aws_object,
                    self.apigw_restapi,
                ]
            )
            self._apigw_authorizer_aws_object_cache = apigw_authorizer
        return self._apigw_authorizer_aws_object_cache

    def apigw_authorizer_lbd_permission_aws_object_pre_check(self):
        """
        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.awslambda.Permission 的条件
        """
        self.lbd_func_aws_object_pre_check()
        self.apigw_authorizer_aws_object_pre_check()

    @property
    def apigw_authorizer_lbd_permission_aws_object(self) -> awslambda.Permission:
        if self.apigw_authorizer_yes is not True:
            return self._apigw_authorizer_lbd_permission_aws_object_cache

        if self._apigw_authorizer_lbd_permission_aws_object_cache is NOTHING:
            apigw_authorizer_lbd_permission_logic_id = "LbdPermission{}".format(self.apigw_authorizer_logic_id)
            apigw_authorizer_lbd_permission = awslambda.Permission(
                title=apigw_authorizer_lbd_permission_logic_id,
                Action="lambda:InvokeFunction",
                FunctionName=GetAtt(self.lbd_func_aws_object, "Arn"),
                Principal="apigateway.amazonaws.com",
                SourceArn=Sub(
                    "arn:aws:execute-api:${Region}:${AccountId}:${RestApiId}/authorizers/${AuthorizerId}",
                    {
                        "Region": {"Ref": "AWS::Region"},
                        "AccountId": {"Ref": "AWS::AccountId"},
                        "RestApiId": Ref(self.apigw_restapi),
                        "AuthorizerId": Ref(self.apigw_authorizer_aws_object),
                    }
                ),
                DependsOn=[
                    self.apigw_authorizer_aws_object,
                    self.lbd_func_aws_object,
                ]
            )
            self._apigw_authorizer_lbd_permission_aws_object_cache = apigw_authorizer_lbd_permission
        return self._apigw_authorizer_lbd_permission_aws_object_cache

    # --- Cloudwatch Event ---
    @property
    def scheduled_job_expression_list(self):
        if self.scheduled_job_expression is NOTHING:
            return self.scheduled_job_expression
        elif isinstance(self.scheduled_job_expression, str):
            return [self.scheduled_job_expression, ]
        elif isinstance(self.scheduled_job_expression, list):
            return self.scheduled_job_expression
        else:
            raise TypeError(
                "{}.cron_job_expression".format(self.identifier)
            )

    def scheduled_job_event_rule_aws_objects_pre_check(self):
        """
        **中文文档**

        检查根据当前的设置, 是否满足自动创建 troposphere_mate.events.Rule 的条件

        目前只支持 CUSTOM 的 Lambda Authorizer

        - :attr:`LbdFuncConfig.scheduled_job_expression`: 必须为Python函数,
            不然没有 Lambda Function 的支持, Event.Rule 就无意义.
        - :attr:`LbdFuncConfig.scheduled_job_expression`: 必须被定义
        - 必须满足所有创建 Lambda Function AWS Object 的条件
        """
        self.lbd_func_aws_object_pre_check()
        if self.scheduled_job_expression is NOTHING:
            raise ValueError("scheduled_job_expression is not defined yet!")

    @property
    def scheduled_job_event_rule_aws_objects(self) -> typing.Dict[str, events.Rule]:
        """
        Returns a key value pair of scheduled job expression and
        ``troposphere_mate.events.Rule`` object. Since
        """
        if self.scheduled_job_yes is not True:
            return self._scheduled_job_event_rule_aws_objects_cache

        if self._scheduled_job_event_rule_aws_objects_cache is NOTHING:
            dct = dict()
            for expression in self.scheduled_job_expression_list:
                event_rule_logic_id = "EventRule{}".format(
                    fingerprint.of_text(expression + self.lbd_func_name)
                )
                event_rule = events.Rule(
                    title=event_rule_logic_id,
                    State="ENABLED",
                    ScheduleExpression=expression,
                    Targets=[
                        events.Target(
                            Id="EventRuleStartCrawlerGitHubDataTrigger",
                            Arn=GetAtt(self.lbd_func_aws_object, "Arn"),
                        )
                    ],
                    DependsOn=[
                        self.lbd_func_aws_object,
                    ]
                )
                dct[expression] = event_rule
            self._scheduled_job_event_rule_aws_objects_cache = dct
        return self._scheduled_job_event_rule_aws_objects_cache

    def scheduled_job_event_lbd_permission_aws_objects_pre_check(self):
        self.scheduled_job_event_rule_aws_objects_pre_check()
        self.lbd_func_aws_object_pre_check()

    @property
    def scheduled_job_event_lbd_permission_aws_objects(self) -> typing.Dict[str, awslambda.Permission]:
        if self.scheduled_job_yes is not True:
            return self._scheduled_job_event_lbd_permission_aws_objects_cache

        if self._scheduled_job_event_lbd_permission_aws_objects_cache is NOTHING:
            dct = dict()
            for expression in self.scheduled_job_expression_list:
                event_rule_lambda_permission_logic_id = "LbdPermissionEventRule{}".format(
                    fingerprint.of_text(expression + self.lbd_func_name)
                )
                event_rule = self.scheduled_job_event_rule_aws_objects[expression]
                event_rule_lambda_permission = awslambda.Permission(
                    title=event_rule_lambda_permission_logic_id,
                    Action="lambda:InvokeFunction",
                    FunctionName=GetAtt(self.lbd_func_aws_object, "Arn"),
                    Principal="events.amazonaws.com",
                    SourceArn=GetAtt(event_rule, "Arn"),
                    DependsOn=[
                        event_rule,
                        self.lbd_func_aws_object,
                    ]
                )
                dct[expression] = event_rule_lambda_permission
            self._scheduled_job_event_lbd_permission_aws_objects_cache = dct
        return self._scheduled_job_event_lbd_permission_aws_objects_cache

    # @property
    # def tp_lbd_environment(self) -> awslambda.Environment:
    #     """
    #
    #     :return:
    #     """
    #     if self.environment_vars is NOTHING:
    #         return self.environment_vars
    #     elif isinstance(self.environment_vars, dict):
    #         return awslambda.Environment(
    #             Variables=self.environment_vars
    #         )
    #     elif isinstance(self.environment_vars, awslambda.Environment):
    #         return self.environment_vars
    #     else:
    #         raise TypeError

    def create_aws_resource(self, template):
        self.create_lbd_func(template)
        self.create_apigw_resource(template)
        self.create_apigw_method(template)
        self.create_apigw_method_options_for_cors(template)

        self.create_apigw_authorizer(template)
        self.create_scheduled_job_event(template)

    def create_lbd_func(self, template: Template):
        try:
            self.lbd_func_aws_object_pre_check()
            template.add_resource(self.lbd_func_aws_object, ignore_duplicate=True)
        except:
            pass

    def create_apigw_resource(self, template: Template):
        try:
            self.apigw_resource_aws_object_pre_check()
            template.add_resource(self.apigw_resource_aws_object, ignore_duplicate=True)
        except:
            pass

    def create_apigw_method(self, template: Template):
        try:
            self.apigw_method_aws_object_pre_check()
            template.add_resource(self.apigw_method_aws_object, ignore_duplicate=True)

            self.apigw_method_lbd_permission_aws_object_pre_check()
            template.add_resource(self.apigw_method_lbd_permission_aws_object, ignore_duplicate=True)
        except:
            pass

    def create_apigw_method_options_for_cors(self, template: Template):
        try:
            self.apigw_method_options_for_cors_aws_object_pre_check()
            template.add_resource(self.apigw_method_options_for_cors_aws_object, ignore_duplicate=True)
        except:
            pass

    def create_apigw_authorizer(self, template: Template):
        try:
            self.apigw_authorizer_aws_object_pre_check()
            template.add_resource(self.apigw_authorizer_aws_object, ignore_duplicate=True)

            self.apigw_authorizer_lbd_permission_aws_object_pre_check()
            template.add_resource(self.apigw_authorizer_lbd_permission_aws_object, ignore_duplicate=True)
        except:
            pass

    def create_scheduled_job_event(self, template: Template):
        try:
            self.scheduled_job_event_rule_aws_objects_pre_check()
            for _, value in self.scheduled_job_event_rule_aws_objects.items():
                template.add_resource(value, ignore_duplicate=True)

            self.scheduled_job_event_lbd_permission_aws_objects_pre_check()
            for _, value in self.scheduled_job_event_lbd_permission_aws_objects.items():
                template.add_resource(value, ignore_duplicate=True)
        except:
            pass


def lbd_func_config_value_handler(module_name: str,
                                  config_field: str,
                                  config_class: typing.Type[LbdFuncConfig],
                                  valid_func_name_list: typing.List[str],
                                  default_lbd_handler_name: str):
    root_module_name = module_name
    for py_current_module, py_parent_module, py_handler_func in walk_lbd_handler(
            module_name, valid_func_name_list):
        # print(py_current_module.__name__)

        current_module_config = getattr(py_current_module, config_field)  # type: LbdFuncConfig
        current_module_config._root_module_name = root_module_name
        current_module_config._py_module = py_current_module
        current_module_config._py_parent_module = py_parent_module

        # print(py_current_module.__name__, py_parent_module.__name__, py_handler_func.__name__)

        if py_handler_func is not None:
            py_handler_func_config = getattr(py_handler_func, config_field)  # type: LbdFuncConfig
            py_handler_func_config._root_module_name = root_module_name
            py_handler_func_config._py_module = py_current_module
            py_handler_func_config._py_parent_module = py_parent_module
            py_handler_func_config._py_function = py_handler_func
            if py_handler_func_config.lbd_func_name is REQUIRED:
                py_handler_func_config.lbd_func_name = \
                    slugify(py_handler_func_config.rel_module_name.replace(".", "-")) + "-" + slugify(
                        py_handler_func.__name__)


def template_creation_handler(module_name: str,
                              config_field: str,
                              config_class: typing.Type[LbdFuncConfig],
                              valid_func_name_list: typing.List[str],
                              template: Template):
    for py_current_module, py_parent_module, py_handler_func in walk_lbd_handler(
            module_name, valid_func_name_list):
        current_module_config = getattr(py_current_module, config_field)  # type: LbdFuncConfig
        current_module_config.create_aws_resource(template)

        if py_handler_func is not None:
            py_handler_func_config = getattr(py_handler_func, config_field)  # type: LbdFuncConfig
            py_handler_func_config.create_aws_resource(template)
