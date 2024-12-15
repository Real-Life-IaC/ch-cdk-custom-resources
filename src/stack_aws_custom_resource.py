import aws_cdk as cdk

from aws_cdk import aws_batch as batch
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from aws_cdk import custom_resources as cr
from constructs import Construct


class StackAwsCustomResource(cdk.Stack):
    """Create a Stack"""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a Batch Fargate Compute Environment
        compute_environment = batch.FargateComputeEnvironment(
            scope=self,
            id="ComputeEnvironment",
            vpc=ec2.Vpc.from_lookup(
                scope=self,
                id="VPC",
                vpc_id=ssm.StringParameter.value_from_lookup(
                    scope=self, parameter_name="/platform/vpc/id"
                ),
            ),
        )

        # Get the ECS Cluster ARN for the compute environment
        cluster = cr.AwsCustomResource(
            scope=self,
            id="BatchEcsCluster",
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
            on_update=cr.AwsSdkCall(
                service="@aws-sdk/client-batch",
                action="DescribeComputeEnvironmentsCommand",
                parameters={
                    "computeEnvironments": [
                        compute_environment.compute_environment_arn,
                    ],
                },
                physical_resource_id=cr.PhysicalResourceId.from_response(
                    "computeEnvironments.0.ecsClusterArn"
                ),
            ),
        )

        # Enable Container Insights for the ECS Cluster
        cr.AwsCustomResource(
            scope=self,
            id="ContainerInsights",
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
            on_update=cr.AwsSdkCall(
                service="@aws-sdk/client-ecs",
                action="UpdateClusterCommand",
                parameters={
                    "cluster": cluster.get_response_field_reference(
                        "computeEnvironments.0.ecsClusterArn"
                    ),
                    "settings": [
                        {
                            "name": "containerInsights",
                            "value": "enabled",
                        },
                    ],
                },
                physical_resource_id=cr.PhysicalResourceId.of(
                    "compute-resource-insights"
                ),
            ),
        )
