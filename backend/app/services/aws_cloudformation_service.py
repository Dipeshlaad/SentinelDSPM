import yaml


SENTINELDSPM_BACKEND_ROLE_ARN = (
    "arn:aws:iam::045511193293:role/SentinelDSPMBackendRole"
)


def generate_aws_onboarding_template(
    account_id: str,
    account_name: str,
    role_name: str,
    external_id: str,
    region: str,
) -> str:

    template = {
        "AWSTemplateFormatVersion": "2010-09-09",

        "Description": (
            "SentinelDSPM AWS onboarding role "
            "for secure read-only AWS data discovery."
        ),

        "Resources": {

            "SentinelDSPMRole": {

                "Type": "AWS::IAM::Role",

                "Properties": {

                    "RoleName": role_name,

                    "Description": (
                        f"SentinelDSPM read-only access for "
                        f"AWS account {account_id} "
                        f"({account_name})"
                    ),

                    "AssumeRolePolicyDocument": {

                        "Version": "2012-10-17",

                        "Statement": [
                            {
                                "Effect": "Allow",

                                "Principal": {
                                    "AWS": SENTINELDSPM_BACKEND_ROLE_ARN
                                },

                                "Action": "sts:AssumeRole",

                                "Condition": {
                                    "StringEquals": {
                                        "sts:ExternalId": external_id
                                    }
                                },
                            }
                        ],
                    },

                    "Policies": [
                        {
                            "PolicyName": "SentinelDSPMS3ReadOnly",

                            "PolicyDocument": {

                                "Version": "2012-10-17",

                                "Statement": [
                                    {
                                        "Effect": "Allow",

                                        "Action": [
                                            "s3:ListAllMyBuckets",
                                            "s3:GetBucketLocation",
                                            "s3:GetBucketVersioning",
                                            "s3:GetBucketEncryption",
                                            "s3:ListBucket",
                                            "s3:GetObject"
                                        ],

                                        "Resource": "*"
                                    }
                                ],
                            },
                        }
                    ],
                },
            }
        },

        "Outputs": {

            "SentinelDSPMRoleName": {
                "Description": "Created IAM role name",
                "Value": {
                    "Ref": "SentinelDSPMRole"
                },
            },

            "SentinelDSPMRoleArn": {
                "Description": "Created IAM role ARN",
                "Value": {
                    "Fn::GetAtt": [
                        "SentinelDSPMRole",
                        "Arn"
                    ]
                },
            },

            "AWSRegion": {
                "Description": "AWS region supplied during onboarding",
                "Value": region,
            },
        },
    }

    return yaml.safe_dump(
        template,
        sort_keys=False
    )