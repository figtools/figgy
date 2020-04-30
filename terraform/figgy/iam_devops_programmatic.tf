### Role to provide devops engineers with programmatic through SSO
module "devops_programmatic" {
  source         = "./modules/account_delegation_role_saml"
  name           = "devops-programmatic"
  mfa            = "true"
  account_id     = var.aws_account_id
  saml_provider = aws_iam_saml_provider.okta.arn
}

####### AWS DevOps Programmatic Policy
resource "aws_iam_policy" "devops_programmatic_access_policy" {
  name        = "devops_programmatic_access"
  description = "DevOps Figgy Programmatic access"
  policy      = data.template_file.dba_programmatic_access_policy_template.rendered
}

data "template_file" "devops_programmatic_access_policy_template" {
  template = templatefile("${path.module}/policies/${var.run_env}/devops_programmatic.json.tpl",
    {
      account_id = var.aws_account_id
      devops_key_arn      = aws_kms_key.devops_key.arn
      run_env             = var.run_env
      config_repl_table   = aws_dynamodb_table.config_replication.arn
      config_audit_table  = aws_dynamodb_table.config_auditor.arn
      config_cache_table  = aws_dynamodb_table.config_cache.arn
    })
}

## Policy attachment
resource "aws_iam_role_policy_attachment" "devops_programmatic_attachment" {
  policy_arn = aws_iam_policy.devops_programmatic_access_policy.arn
  role       = module.devops_programmatic.name
}
