import boto3


SENTINELDSPM_BACKEND_ROLE_ARN = (
    "arn:aws:iam::045511193293:role/SentinelDSPMBackendRole"
)


def get_customer_s3_client(
    account_id: str,
    role_name: str,
    external_id: str,
    region: str,
):

    customer_role_arn = (
        f"arn:aws:iam::{account_id}:role/{role_name}"
    )

    sts = boto3.client("sts")

    backend_credentials = sts.assume_role(
        RoleArn=SENTINELDSPM_BACKEND_ROLE_ARN,
        RoleSessionName="SentinelDSPMBackendDiscovery",
    )["Credentials"]

    backend_sts = boto3.client(
        "sts",
        aws_access_key_id=backend_credentials["AccessKeyId"],
        aws_secret_access_key=backend_credentials["SecretAccessKey"],
        aws_session_token=backend_credentials["SessionToken"],
    )

    customer_credentials = backend_sts.assume_role(
        RoleArn=customer_role_arn,
        RoleSessionName="SentinelDSPMCustomerDiscovery",
        ExternalId=external_id,
    )["Credentials"]

    return boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=customer_credentials["AccessKeyId"],
        aws_secret_access_key=customer_credentials["SecretAccessKey"],
        aws_session_token=customer_credentials["SessionToken"],
    )


def discover_s3_buckets(
    account_id: str,
    role_name: str,
    external_id: str,
    region: str,
):

    s3 = get_customer_s3_client(
        account_id=account_id,
        role_name=role_name,
        external_id=external_id,
        region=region,
    )

    response = s3.list_buckets()

    return response["Buckets"]


def discover_s3_objects(
    s3_client,
    bucket_name: str,
):

    objects = []

    paginator = s3_client.get_paginator(
        "list_objects_v2"
    )

    for page in paginator.paginate(
        Bucket=bucket_name
    ):
        for obj in page.get("Contents", []):

            objects.append(
                {
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"],
                }
            )

    return objects

def read_s3_object(
    s3_client,
    bucket_name: str,
    object_key: str,
):

    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_key,
    )

    content = response["Body"].read()

    return content.decode("utf-8")

def normalize_s3_objects(
    objects: list,
    bucket_name: str,
):
    normalized_objects = []

    for obj in objects:

        key = obj["key"]

        if "." in key.rsplit("/", 1)[-1]:
            file_type = (
                key.rsplit("/", 1)[-1]
                .rsplit(".", 1)[-1]
                .lower()
            )
        else:
            file_type = "unknown"

        normalized_objects.append(
            {
                "name": key.rsplit("/", 1)[-1],
                "type": file_type,
                "path": f"s3://{bucket_name}/{key}",
                "size": obj["size"],
                "last_modified": obj["last_modified"],
            }
        )

    return normalized_objects

def read_s3_object_bytes(
    s3_client,
    bucket_name: str,
    object_key: str,
):
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_key,
    )

    return response["Body"].read()