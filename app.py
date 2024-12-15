import aws_cdk as cdk

from src.stack_aws_custom_resource import StackAwsCustomResource
from src.stack_external_custom_resource import StackExternalCustomResource


app = cdk.App()
StackAwsCustomResource(
    scope=app,
    id="StackAwsCustomResource",
    env=cdk.Environment(account="637423243766", region="us-east-1"),
)

StackExternalCustomResource(
    scope=app,
    id="StackDatabricksCustomResource",
    env=cdk.Environment(account="637423243766", region="us-east-1"),
)
app.synth()
