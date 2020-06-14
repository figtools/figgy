These are problems I intend to solve, once I figure out the best way to do it.

## Todo:
- Add config flag around anonymous metric tracking
- Test release rollback
- Add version to anonymous tracking
- Implement validate command
- `figgy config get --role dev` fails with sandbox login.
- Double check. Deletes don't seem to be showing up in slack webhook
- CW alarms for lambdas
- Create sample application that shows CICD validation.
- Verify `replication_config` enforces shared namespace
- Test sync with `/app/multi/level/twig/`
- Add automated test with replicate from
- Automated test with merge-params
- Tag all SSM params with managed_by: figgy
- `figgy --reset` or `figgy reset`

## Ideas:
- Remove need for users to have allow 'Python'
- Personal passpack by using tags.

- Add support for "ExternalId" verification for cross-account role assumption from Bastion.
- Param finder
- Figgy Experimental
- Unused parameter recommender
- 1 time password share-er
- Encrypted event batching & backup to s3
