# -*- coding: utf-8 -*-

import troposphere_mate as tm
from troposphere_mate import apigateway, awslambda, iam
from troposphere_mate.canned.iam import AWSManagedPolicyArn, AWSServiceName, create_assume_role_policy_document

template = tm.Template()

param_env_name = tm.Parameter(
    "EnvironmentName",
    Type="String",
)
template.add_parameter(param_env_name)

rest_api = apigateway.RestApi(
    "RestApi",
    template=template,
    Name=tm.helper_fn_sub("{}-py", param_env_name),
    EndpointConfiguration=apigateway.EndpointConfiguration(
        Types=["REGIONAL", ]
    )
)

lambda_code = awslambda.Code(
    S3Bucket="eq-sanhe-for-everything",
    S3Key="lambda/MacHu-GWU/lbdrabbit-project/0.0.1/source.zip",
)

iam_role = iam.Role(
    "IamRoleForLbdFunc",
    template=template,
    RoleName=tm.helper_fn_sub("{}-lbd-func", param_env_name),
    AssumeRolePolicyDocument=create_assume_role_policy_document([
        AWSServiceName.aws_Lambda
    ]),
    ManagedPolicyArns=[
        AWSManagedPolicyArn.awsLambdaBasicExecutionRole
    ]
)
