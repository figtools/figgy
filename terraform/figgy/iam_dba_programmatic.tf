### Role to provide DBAs with programmatic through SSO
module "dba_programmatic" {
  source         = "./modules/account_delegation_role_saml"
  name           = "dba-programmatic"
  mfa            = "true"
  account_id     = var.aws_account_id
  saml_provider = aws_iam_saml_provider.okta.arn
}

#############################################
####### AWS DBA Programmatic Policy  ########
#############################################
resource "aws_iam_policy" "dba_programmatic_access_policy" {
  name        = "dba_programmatic_access"
  description = "DBA Figgy Programmatic access"
  policy      = data.template_file.dba_programmatic_access_policy_template.rendered
}

data "template_file" "dba_programmatic_access_policy_template" {
  template = templatefile("${path.module}/policies/${var.run_env}/dba_programmatic.json.tpl",
    {
      account_id = var.aws_account_id
      dba_key_arn         = aws_kms_key.dba_key.arn
      run_env             = var.run_env
      config_repl_table   = aws_dynamodb_table.config_replication.arn
      config_audit_table  = aws_dynamodb_table.config_auditor.arn
      config_cache_table  = aws_dynamodb_table.config_cache.arn
    })
}

## Policy attachment
resource "aws_iam_role_policy_attachment" "dba_programmatic_attachment" {
  policy_arn = aws_iam_policy.dba_programmatic_access_policy.arn
  role       = module.dba_programmatic.name
}

