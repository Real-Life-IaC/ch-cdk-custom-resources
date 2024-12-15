import aws_cdk as cdk

from src.stack_aws_custom_resource import StackAwsCustomResource


app = cdk.App()
StackAwsCustomResource(
    scope=app,
    id="StackAwsCustomResource",
    env=cdk.Environment(account="637423243766", region="us-east-1"),
)
app.synth()
