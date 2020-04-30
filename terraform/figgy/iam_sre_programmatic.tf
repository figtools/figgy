### Role to provide site reliability engineers with programmatic through SSO
module "sre_programmatic" {
  source         = "./modules/account_delegation_role_saml"
  name           = "sre-programmatic"
  mfa            = "true"
  account_id     = var.aws_account_id
  saml_provider = aws_iam_saml_provider.okta.arn
}

#############################################
####### AWS Data Programmatic Policy  ########
#############################################
resource "aws_iam_policy" "sre_programmatic_access_policy" {
  name        = "sre_programmatic_access"
  description = "SRE Figgy Programmatic access"
  policy      = data.template_file.sre_programmatic_access_policy_template.rendered
}

data "template_file" "sre_programmatic_access_policy_template" {
  template = templatefile("${path.module}/policies/${var.run_env}/sre_programmatic.json.tpl",
    {
      account_id = var.aws_account_id
      sre_key_arn         = aws_kms_key.sre_key.arn
      run_env             = var.run_env
      config_repl_table   = aws_dynamodb_table.config_replication.arn
      config_audit_table  = aws_dynamodb_table.config_auditor.arn
      config_cache_table  = aws_dynamodb_table.config_cache.arn
    })
}

## Policy attachment
resource "aws_iam_role_policy_attachment" "sre_programmatic_attachment" {
  policy_arn = aws_iam_policy.sre_programmatic_access_policy.arn
  role       = module.sre_programmatic.name
}