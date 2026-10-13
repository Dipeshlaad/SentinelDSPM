import boto3


SENTINELDSPM_BACKEND_ROLE_ARN = (
    "arn:aws:iam::045511193293:role/SentinelDSPMBackendRole"
)


def verify_aws_account_connection(
    account_id: str,
    role_name: str,
    external_id: str,
    region: str,
) -> bool:

    customer_role_arn = (
        f"arn:aws:iam::{account_id}:role/{role_name}"
    )

    sts = boto3.client("sts")

    backend_credentials = sts.assume_role(
        RoleArn=SENTINELDSPM_BACKEND_ROLE_ARN,
        RoleSessionName="SentinelDSPMBackendVerification",
    )["Credentials"]

    backend_sts = boto3.client(
        "sts",
        aws_access_key_id=backend_credentials["AccessKeyId"],
        aws_secret_access_key=backend_credentials["SecretAccessKey"],
        aws_session_token=backend_credentials["SessionToken"],
    )

    customer_credentials = backend_sts.assume_role(
        RoleArn=customer_role_arn,
        RoleSessionName="SentinelDSPMCustomerVerification",
        ExternalId=external_id,
    )["Credentials"]

    s3 = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=customer_credentials["AccessKeyId"],
        aws_secret_access_key=customer_credentials["SecretAccessKey"],
        aws_session_token=customer_credentials["SessionToken"],
    )

    s3.list_buckets()

    return True