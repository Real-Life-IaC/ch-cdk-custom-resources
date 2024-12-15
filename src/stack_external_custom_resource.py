import aws_cdk as cdk

from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import custom_resources as cr
from constructs import Construct


class StackExternalCustomResource(cdk.Stack):
    """Create a Stack"""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(
            scope=self,
            id="DatabricksStorageBucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        secret = secretsmanager.Secret.from_secret_name_v2(
            scope=self,
            id="DatabricksServicePrincipalSecret",
            secret_name="/databricks/service-principal/cdk",  # nosec: B106
        )

        lambda_function = _lambda.DockerImageFunction(
            scope=self,
            id="DatabricksApiFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="assets/databricks_provider_lambda/",
            ),
        )

        secret.grant_read(lambda_function)

        provider = cr.Provider(
            scope=self,
            id="DatabricksProvider",
            on_event_handler=lambda_function,
        )

        cdk.CustomResource(
            scope=self,
            id="DatabricksStorageConfiguration",
            service_token=provider.service_token,
            properties={
                "DatabricksResource": "StorageConfiguration",
                "DatabricksResourceName": "DatabricksStorageConfiguration",
                "DatabricksBucketName": bucket.bucket_name,
            },
        )
