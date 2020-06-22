Figgy Changelog:

## 0.0.32
- Testing release pipeline through pypi, brew, etc.

## 0.0.31
- Adding support for `--profile` optional parameter that overrides all authentication schemes and authorizes 
only with the user's locally configured & targeted AWSCLI profile. This will be very useful for CICD builds and for
some teams who only have a single AWS account.

- Renaming `figgy` package to `figcli` to prevent name collission shenanigans with the new `figgy-lib` package. 

## 0.0.30a
- Naming figgy.json properties to their new 'figgy'names.

## 0.0.29a
- Fixing a bug with `figgy --configure` when configuring a bastion account for the first time.

## 0.0.28a
- Making `config list` command leverage RBAC limited config view for improved performance.

## 0.0.27a
- Continued Testing of release process
- Plus some other stuff!
- And some other stuff!

## 0.0.1a
- First version!

