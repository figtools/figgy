{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "KmsDecryptPermissions",
            "Effect": "Allow",
            "Action": [
                "kms:DescribeKey",
                "kms:Decrypt"
            ],
            "Resource": [
               "${dba_key_arn}"
           ]
        },
        {
            "Sid": "KmsEncryptPermissions",
            "Effect": "Allow",
            "Action": [
                "kms:Encrypt"
            ],
            "Resource": "${dba_key_arn}"
        },
        {
            "Sid": "ListKeys",
            "Effect": "Allow",
            "Action": [
                "kms:ListKeys"
            ],
            "Resource": "*"
        },
        {
            "Sid": "SSMPerms",
            "Effect": "Allow",
            "Action": [
                "ssm:DeleteParameter",
                "ssm:DeleteParameters",
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:GetParameterHistory",
                "ssm:GetParametersByPath",
                "ssm:PutParameter"
            ],
            "Resource": [
                "arn:aws:ssm:*:${account_id}:parameter/shared/*",
                "arn:aws:ssm:*:${account_id}:parameter/app/*",
                "arn:aws:ssm:*:${account_id}:parameter/dba/*"
            ]
        },
        {
            "Sid": "SSMDescribe",
            "Effect": "Allow",
            "Action": [
                "ssm:DescribeParameters"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "ConfigReplAccess",
            "Effect": "Allow",
            "Action": [
                "dynamodb:Get*",
                "dynamodb:List*",
                "dynamodb:Put*",
                "dynamodb:Delete*",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
                "dynamodb:UpdateTimeToLive"
            ],
            "Resource": [
                "${config_repl_table}"
            ]
        },
        {
            "Sid": "AuditLogRead",
            "Effect": "Allow",
            "Action": [
                "dynamodb:Get*",
                "dynamodb:List*",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "${config_audit_table}",
                "${config_repl_table}",
                "${config_cache_table}"
            ]
        }
    ]
}