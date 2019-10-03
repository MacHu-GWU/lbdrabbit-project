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
    ApiMethodIntType._valid_values.add(v)


@attr.s
class LbdFuncConfig(BaseConfig):
    """
    Lambda Function Level Config.

    Every child function under a resource inherits :class:`ResourceConfig``.


    :param apigw_authorizer_yes: indicate if this lambda function is used
        as a custom authorizer.

    **中文文档**


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

    apigw_method_int_passthrough_behavior = attr.ib(default=NOTHING)  # type: str
    apigw_method_int_timeout_in_milli = attr.ib(default=NOTHING)  # type: int
    apigw_method_authorization_type = attr.ib(default=NOTHING)  # type: str
    apigw_method_authorizer = attr.ib(default=NOTHING)  # type: apigateway.Authorizer

    apigw_authorizer_yes = attr.ib(default=NOTHING)  # type: bool
    apigw_authorizer_name = attr.ib(default=NOTHING)  # type: bool
    _apigw_authorizer_aws_object_cache = attr.ib(default=NOTHING)  # type: apigateway.Authorizer
    _apigw_authorizer_lbd_permission_aws_object_cache = attr.ib(default=NOTHING)  # type: awslambda.Permission

    scheduled_job_yes = attr.ib(default=NOTHING)  # type: bool
    scheduled_job_expression = attr.ib(default=NOTHING)  # type: typing.Union[str, typing.List[str]]
    _scheduled_job_event_rule_aws_objects_cache = attr.ib(default=NOTHING)  # type: typing.Dict[str, events.Rule]
    _scheduled_job_event_lbd_permission_aws_objects_cache = attr.ib(
        default=NOTHING)  # type: typing.Dict[str, awslambda.Permission]

    _root_module_name = attr.ib(default=NOTHING)
    _py_module = attr.ib(default=NOTHING)
    _py_parent_module = attr.ib(default=NOTHING)
    _py_function = attr.ib(default=NOTHING)

    _default = dict(
        lbd_func_yes=True,
        memory_size=128,
        timeout=3,
        apigw_resource_yes=False,
        apigw_method_yes=False,
        apigw_method_int_passthrough_behavior="WHEN_NO_MATCH",
        apigw_method_int_timeout_in_milli=29000,
        apigw_authorizer_yes=False,
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

    @property
    def lbd_func_logic_id(self) -> str:
        return "LbdFunc{}".format(
            camelcase(self.rel_module_name.replace(".", "-"))
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

    @property
    def lbd_func_aws_object(self) -> awslambda.Function:
        if self.lbd_func_yes is not True:
            return self._lbd_func_aws_object_cache

        if callable(self._py_function):
            try:
                self._py_function.__name__
            except AttributeError:
                raise TypeError("{}.{} is not a valid function".format(self._py_module.__name__, self._py_function))
        else:
            raise TypeError("{}.{} is not a valid function".format(self._py_module.__name__, self._py_function))

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
        return slugify(self._py_module.__name__.split(".")[-1])

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
            camelcase(self.rel_module_name.replace(".", "-"))
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
    def apigw_method_aws_object(self) -> apigateway.Method:
        if self.apigw_method_yes is not True:
            return self._apigw_method_aws_object_cache

        if self._apigw_method_aws_object_cache is NOTHING:
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
                ]
            )
            if self.apigw_method_int_passthrough_behavior is not NOTHING:
                integration.PassthroughBehavior = self.apigw_method_int_passthrough_behavior
            if self.apigw_method_int_timeout_in_milli is not NOTHING:
                integration.TimeoutInMillis = self.apigw_method_int_timeout_in_milli

            self.check_apigw_method_authorization_type()
            self.check_apigw_method_int_type()

            apigw_method = apigateway.Method(
                title=self.apigw_method_logic_id,
                RestApiId=Ref(self.apigw_restapi),
                ResourceId=Ref(self.apigw_resource_aws_object),
                AuthorizationType=self.apigw_method_authorization_type,
                HttpMethod="POST",
                MethodResponses=[
                    apigateway.MethodResponse(
                        StatusCode="200",
                        ResponseModels={"application/json": "Empty"},
                    )
                ],
                Integration=integration,
                DependsOn=[
                    self.apigw_resource_aws_object,
                    self.lbd_func_aws_object,
                ]
            )

            if self.apigw_method_authorizer is not NOTHING:
                apigw_method.AuthorizerId = Ref(self.apigw_method_authorizer)

            self._apigw_method_aws_object_cache = apigw_method
        return self._apigw_method_aws_object_cache

    @classmethod
    def get_authorizer_id(cls, rel_module_name):
        return "ApigwAuthorizer{}".format(
            camelcase(rel_module_name.replace(".", "-"))
        )

    @property
    def apigw_authorizer_logic_id(self) -> str:
        return self.get_authorizer_id(self.rel_module_name)

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
                IdentitySource="method.request.header.auth",
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
                event_rule_logic_id = "EventRule{}".format(fingerprint.of_text(expression))
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

    @property
    def scheduled_job_event_lbd_permission_aws_objects(self) -> typing.Dict[str, awslambda.Permission]:
        if self.scheduled_job_yes is not True:
            return self._scheduled_job_event_lbd_permission_aws_objects_cache

        if self._scheduled_job_event_lbd_permission_aws_objects_cache is NOTHING:
            dct = dict()
            for expression in self.scheduled_job_expression_list:
                event_rule_lambda_permission_logic_id = "EventRuleLbdPermission{}".format(
                    fingerprint.of_text(expression)
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


@property
def tp_lbd_environment(self) -> awslambda.Environment:
    """

    :return:
    """
    if self.environment_vars is NOTHING:
        return self.environment_vars
    elif isinstance(self.environment_vars, dict):
        return awslambda.Environment(
            Variables=self.environment_vars
        )
    elif isinstance(self.environment_vars, awslambda.Environment):
        return self.environment_vars
    else:
        raise TypeError


def create_aws_resource(self, template):
    self.create_lbd_func(template)
    self.create_apigw_resource(template)


def create_lbd_func(self, template):
    pass


def create_apigw_resource(self, template):
    if self.apigw_resource_yes:
        logic_id = ""
        api_resource = apigateway.Resource(
            logic_id,
            ParentId="",
            PathPart=self.apigw_resource_path_part,
            RestApiId=Ref(self.apigw_restapi),
        )


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

        # # apigw_resource_parent_id
        # if not len(rel_module_name): # root module
        #     apigw_resource_parent_id = GetAtt(current_module_config.apigw_restapi, "RootResourceId")
        # else:
        #     pass

        # apigw_resource_path_part
        # apigw_resource_path_part = slugify(py_current_module.__name__.split(".")[-1])
        # if current_module_config.apigw_resource_path_part is NOTHING:
        #     current_module_config.apigw_resource_path_part = apigw_resource_path_part

        # if py_handler_func_config.apigw_reso
        # urce_path_part is NOTHING:
        #     py_handler_func_config.apigw_resource_path_part = apigw_resource_path_part
        #
        # if py_handler_func.__name__ == default_lbd_handler_name:
        #     function_name = slugify(rel_module_name.replace(".", "-"))
        # else:
        #     function_name = slugify(rel_module_name.replace(".", "-") + "-" + py_handler_func.__name__)
        # if py_handler_func_config.lbd_func_name is NOTHING:
        #     py_handler_func_config.lbd_func_name = function_name


def template_creation_handler(module_name: str,
                              config_field: str,
                              config_class: typing.Type[LbdFuncConfig],
                              valid_func_name_list: typing.List[str],
                              template: Template):
    for py_current_module, py_parent_module, py_handler_func in walk_lbd_handler(
            module_name, valid_func_name_list):
        # print(py_current_module.__name__)
        current_module_config = getattr(py_current_module, config_field)  # type: LbdFuncConfig
        current_module_config.create_aws_resource(template)
