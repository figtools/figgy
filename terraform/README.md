#### What you need to update

This is a terraform "multi-environment" deployment. You will want to run this configuration against each account
you intend to provision Figgy for. For each environment, you'll want to update the variables files here:

variables/{ENV}/vars.tfvars

If you wish to choose different environment names that is 100% ok, just be sure to update the var file names and the 
`Figgy` configs to match these new names you've selected here. Also, if you are configuring SSO, you will want to 
make sure you saml/metadata-${RUN_ENV}.xml files match your new environment names.


Files you may need to update to configure Figgy deployment to your AWS account(s):

figgy/A_configure_figgy.tf
figgy/main.tf
figgy/vars/dev.tfvars
figgy/vars/qa.tfvars
figgy/vars/stage.tfvars
figgy/vars/prod.tfvars
figgy/vars/mgmt.tfvars

#### Command workflow

To setup the workspace for a particular run environment:

`terraform workspace new dev`

To swap workspaces

`terraform workspace select dev`

To perform a plan:

`terraform plan -var-file=vars/dev/vars.tfvars`

To perform an apply:

`terraform apply -var-file=vars/dev.tfvars`