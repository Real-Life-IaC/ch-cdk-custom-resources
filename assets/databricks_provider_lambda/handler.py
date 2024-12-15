import json

import boto3

from databricks.sdk import AccountClient
from databricks.sdk.service import provisioning


secrets_manager_client = boto3.client("secretsmanager")


def lambda_handler(event: dict, context: dict) -> dict:
    """Lambda handler"""

    request_type = event["RequestType"]
    databricks_resource = event["ResourceProperties"]["DatabricksResource"]
    databricks_resource_name = event["ResourceProperties"][
        "DatabricksResourceName"
    ]
    databricks_bucket_name = event["ResourceProperties"][
        "DatabricksBucketName"
    ]

    # Note that we need to create an account in Databricks
    # and then create this secret in the Secrets Manager before running the stack
    secret = json.loads(
        secrets_manager_client.get_secret_value(
            SecretId="/databricks/service-principal/cdk"
        )["SecretString"]
    )

    # Authenticate with Databricks
    account_client = AccountClient(
        host="https://accounts.cloud.databricks.com",
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
        account_id=secret["account_id"],
    )

    if databricks_resource == "StorageConfiguration":
        if request_type == "Create":
            # Create a storage configuration
            # and return the storage configuration id
            storage = account_client.storage.create(
                storage_configuration_name=databricks_resource_name,
                root_bucket_info=provisioning.RootBucketInfo(
                    bucket_name=databricks_bucket_name
                ),
            )
            return {"PhysicalResourceId": storage.storage_configuration_id}
        elif request_type == "Update":
            # DataBricks does not support updating storage configurations
            return {"PhysicalResourceId": event["PhysicalResourceId"]}
        else:
            # Delete the storage configuration
            account_client.storage.delete(
                storage_configuration_id=event["PhysicalResourceId"]
            )

            return {"PhysicalResourceId": event["PhysicalResourceId"]}
    else:
        raise ValueError("Unsupported Databricks resource")
