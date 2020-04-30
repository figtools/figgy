Figgy Changelog:

## 1.11.3
- Forcing release of figgy to verify auto-upgrade fix and figgy change to support one-dir mode instead of one-file mode.

## 1.11.2
- Add `pao-programmatic` role support for managing PleaseApplyOnline S3 buckets
- Adding support to auto-upgrade for OS X "onedir" installs.

## 1.11.1
- Fixing a bug with `figgy config get` whereby parameters with > 50 versions would not always print out the value as the 50th version. This bug 
was introduced in version `1.10.0` when changing the `get` command to output parameter descriptions alongside their values.

## 1.11.0
- Adding `figgy cicd deploy` command to allow "beta" version of submitting groups of deployments
- Adding `figgy config generate` command to simplify generating new service configurations.
- Adding support for  `replicate_from` block to `figgy`. Changes were made to `sync`, `cleanup`

## 1.10.6
- Add partial support for the data scale accounts: `iam export`, `tfe auth`, and some `config` features

## 1.10.5
- Adding `--copy-from` flag for `sync` command to make it easier to have multiple service deployments under
different namespaces from the same source repository and codebase.

## 1.10.4
- Increasing max pool size for boto3 s3 connection pools. This will reduce pool warning messages and should,
in theory, improve performance on highly concurrent s3 api operations, though I haven't been able to to prove
a performance improvementt.
- Fixing bug with cleanup command's auto-default of `--config` flag

## 1.10.3
- `config` commands should now bootstrap at __least__ 1 second faster due to now 
leveraging multiple layers of cache for auto completion, and only querying for cache differences between
invocations. 

## 1.10.2
- Improved `figgy s3 find` tuning around an edge case where the user specifies a s3 path that has tens or hundreds of
thousands of subdirectories within it.

## 1.10.1
- Improving performance of `figgy s3 find` command when attempting to search MASSIVE directories of files 
(hundreds of thousands)
- Adding progress bar for file list aggregation phase of `figgy s3 find` command
- Adding support for filtering files that will be searched by matching file-name patterns. (e.g. "Search all files in 
folder X that have `2020_02` in their names")


## 1.10.0
- Added new `figgy config edit` command that will now allow you to multi-line edit OR ADD new configs!
- `figgy config put` will now never overwrite the existing `description` if it was not specified with the new `put`.
- `browse` and `get` commands will now display descriptions, or `Not specified` if a description is missing.
- `figgy` will now auto-abort if you run it as root. DO NOT RUN Figgy AS ROOT. 

## 1.9.1
- Lots of enhancements based on user recommendations - Check them out!
- Improving validation for `figgy cicd run-tests`
- Adding support for `figgy --configure` to allow setting a default account that will be respected.
- Adding auto-default of `--config` flag to be `./ci-config.json` for `sync` and `cleanup` commands.
- Adding support for --prefix optional parameter to browse command. `figgy config browse --prefix /app/foo` will now
build a browse tree with only values found under `/app/foo`. This also improves browse performance.

## 1.9.0
- Adding new `figgy cicd run-tests` command to enable auto-kicking off integration tests through our QE Test Runner pipeline.

## 1.8.15
- `figgy` error auto-reporting via SNS will now lookup the users OKTA ID and report it in the error message
rather than looking up the user's computer user id. This fixes issues with the "root" being reported as the 
user when people run figgy as root.

## 1.8.14
- Add partial support for the data science accounts: `iam export`, `tfe auth`, and some `config` features

## 1.8.12
- Attempting to fix a difficult to-troubleshoot issue with the built windows binary.

## 1.8.11
- Fixing a bug with s3 find where the trailing whitespace in the search folder path could cause a division by 0 error.
- (related) Fixed a bug where a division by 0 error could be caused when an invalid folder was specified that had no files found
in s3.

## 1.8.10
- Adding output that indicates the # of files that were `skipped` when using the `s3 find` command. Also fixing a bug
that cause CSV files with capitalized extensions to be skipped and not searched.

## 1.8.9
- Fixing bug introduced in 1.8.8 that broke `log tail` functionality.

## 1.8.8
- Performance tuning improvements for the `config` resource init process by leveraging multi-threading more
effectively while initializing. 

## 1.8.7
- Improving intuitiveness of `figgy config restore --point-in-time` command. Changing prompts to ask WHAT to restore before asking when.

## 1.8.6
- Fixing a tiny display bug with `s3 zip` where the progress bar could be at 99% but the Zip successful message already displayed.

## 1.8.5
- Adding progress bar for `s3 zip` command.
- Addressing lock contention issues within the `zip` library that was slowing write speeds.

## 1.8.4
- Improving performance of the `s3 find` and adding progress bars.

## 1.8.3
- Improving multi-threaded performance for the `s3 find` command. Also fixing a bug where find could potentially not match
properly against larger files. 

## 1.8.2
- Fixing an issue with auto-upgrade auto-complete when the `figgy` binary happens to be installed in a directory named `figgy`

## 1.8.1
- Fixing a bug with the `s3 find` command that caused it to skip searching some files when it should have searched.

## 1.8.0
- Adding new command `s3 zip`. This will zip up any arbitrary directory in s3 by downloading batches of files across
many threads and zipping them up locally. Great for downloading thousands, or hundreds of thousands of files
from s3 and saving locally!

## 1.7.3
- Updating `log tail` to have a `--service` optional parameter instead of `--tag` for live tailing logs for a particular
service.

## 1.7.2
- Cleaning up debug logging and fixing issue with debug logging sometimes being printed out without the --debug flag.

## 1.7.1
- Fixing bug with optional flags passed in with `store_true` actions. This bug caused some flags such as --all-profiles
to not be registered properly.

## 1.7.0
- Adding new `s3` resource and `find` command for recursively searching through the contents of files in S3. 
- Major refactoring of how `figgy` initializes to improve readability and maintainability of this repository.
- Adding `--debug` flag to allow output of debug logging at will

## 1.6.14
- Fixing a bug with windows upgrades. We were accidentally downloading the figgy twice which would _sometimes_ cause
upgrade issues due to a race condition. OOPS! #sorrynotsorry #actuallyreallysorry #mybadchrismcccord

## 1.6.13
- Fixing a new bug where the `get` command can throw stack traces when attempting to fetch values encrypted with KMS
keys ther user does not have access to.

## 1.6.12
- Fixing a bug introduced in 1.6.8 with the sync command when running sync in production as the `dev` role against configs
encrypted with the application KMS key. The user will no longer be prompted to reset already set non-replicated 
application secrets.

## 1.6.11
- Improving how figgy handles password updates when users update their OKTA passwords. Users will no longer be required
to run `figgy --configure`, instead figgy should prompt the user for their password and overwrite the old password
in the keychain.

## 1.6.10
- Nothing here. Forcing a new version to verify autoupgrade is FINALLY FIXED.

## 1.6.9
- Fixing a bug with windows autoupgrade exploding when coming across a previous build's tmp file.

## 1.6.8
- Adding support for `file:///` prefix when running figgy config sync.

## 1.6.7
- Adding not-advertised support to `promote` command for passing in a full path to a parameter and not a prefix.
- Fixing bug with --info sub parameters. Also fixing rare bug in sync command.

## 1.6.6
- Adding auto-completed cache for service-names when running `figgy log tail` to help find the right service to tail.
- Fixing but with auto-upgrade feature

## 1.6.5
- Add `--role` argument support for most commands

## 1.6.4
- Fixing bug with config.json validation when namespace is missing and app_parameters is missing namespace in parmater 
names

## 1.6.3
- Removing accidental printed log message

## 1.6.2
- Improving `figgy log tail` output format if the `message` field is missing.

## 1.6.1
- Fixing but with `figgy log restore` introduced by the introduction of the tail command. `restore` was always broken. 

## 1.6.0
- Adding `tail` command for `log` resource
- Adding `--all` flag to `figgy iam export`. This will export temporary credentials to all accounts under different
aws cli profiles.

## 1.5.0
- Adding the new `log` resource with the `restore` command. This resource enables
devops users to restore logs from a specified timeframe for a specified environment back to loggly.

## 1.4.5
- Fixing an issue with figgy restore for some parameter restore attemps.

## 1.4.4
- Adding wildcard (*) support for `figgy tfe auth` command to support pushing credentials to multiple workspaces.

## 1.4.3
- Updating iam export to automatically create ~/.aws/credentials and ~/.aws/config files if they don't already exist. This removes the dependency on the `awscli` 

## 1.4.2
- Fixing an issue with sync in prod when assumed as a developer role. Sync cannot complete with application key encrypted parameters
since engineers cannot decrypt app-key encrypted parameters in production.

## 1.4.1
- Fixing a bug where if a user *improperly* entered their MFA after their previous OKTA session expired, they would get a stacktrace
instead of just being prompted to re-enter their MFA again.

## 1.4.0
- Adding support for OKTA and removing support for MGMT user long duration credentials.
- Added support for `figgy iam export --env mgmt` (mgmt credentials export - useful for ecr authentication)

## 1.3.1
- Fixing a bug with promoting when supplied --env parameter is `prod` (which is invalid).
- Introducing a new validation type with `figgy cicd validate`

## 1.3.0
- Adding `promote` command to `config` resource. Promote parameters between Dev -> Qa -> UAT -> Prod with `figgy config promote --env {env}`!

### 1.2.2
- Removing a logging statement that was accidentally built into 1.2.1 >.>

### 1.2.1
- Various improvements with help text. Typo fixes, etc.

### 1.2.0
- Adding new "tfe" resource. This will provide functionality when interacting with Terraform Enterprise.
- New "tfe" command "auth" added. This will push temporary credentials to a selected TFE workspace.
- `figgy tfe auth`

### 1.1.0
- Adding new "cicd" resource. This will be used to add lots of functionality around pipelines! Yay!
- Adding "validate" command to "cicd" resource. This is used by DevOps only for plugin validation purposes. Yay!

### 1.0.29
- Fixing a bug with `sync --replication-only` after improved validation added in 1.0.27

### 1.0.28
- Fixing an issue introduced in 1.0.27 that broke defaulting of environment to the DEV environment if no --env parameter is specified.

### 1.0.27
- Improving load time for browse even more!
- Fixed a bug with sync/cleanup when removing a previously existing merge parameter
- Improving validation of merge / replication configurations to enforce the destination must be in your app namespace

### 1.0.26
- Fixing a bug where a stacktrace would be thrown when the <command> parameter was missing. Improving validation / error messaging around this case.
- Improving load time of browse command by like 10x by leveraging a dynamo cache instead of paginating through SSM parameter list calls.

### 1.0.25
- Adding support for `iam` resource and `export` command. You may now export temporary sts tokens to your ~/.aws/credentials default profile.
- Improving error messaging around a error thrown when a user doesn't have any MFA devices associated with their programmatic user.

### 1.0.24
- Orphaned configurations will no longer cause the `sync` error message to trigger.

### 1.0.23
- Fixing bug with autocomplete where you would see duplicate auto-complete suggestions when overwriting a value with put.

### 1.0.22
- Adding restore command functionality

### 1.0.21
- Sorting cached Parameter store names when they come out of DDB so they are properly ordered with word complete suggestions.

### 1.0.20
- Fixing a bug where an exception is thrown when users forget to specify both an app_parameters and a namespace block in 
their ci-config.json

### 1.0.19
- Removing a print command that is logging potential secrets to console. It was accidentally uncommented while debugging.

### 1.0.18
- Major refactorings of loading of parameter names for auto-complete suggestions and browse tree population. 
Fetching parameter names was previously synchronous through paginated APIs. New DDB cache table implemented that is 
populated via cloudwatch event streams.
- Fixing a couple bugs discovered with the `migrate` command.
- Slight migrate refactorings for prefix as an instance variable - courtesy of gonyo.
- Adding significant migrate E2E tests to cover edge cases. These cannot be run in circle ci and are only run locally.
- Fixing a migrate bug for STAGE / Prod migrates (a misconfiguration in config.py)

### 1.0.17
- Updating ci-config.json parser to catch JSON Decode errors and print a pretty error message instead of
a stack trace.

### 1.0.16
- Fixing a few bugs related to `config migrate` introduced by 1.0.15
- Updating auto-upgrade to properly guestimate the default path (courtesy of gonyo)

### 1.0.15
- Making browse SORT hierarchies alphabetically. 
- Fixing bug with migrate when opting for an empty namespace_suffix
- Fixing a bug with  migrating a single value with --manual flag.

### 1.0.14
- Fixing a typo that broke browse.

### 1.0.13
- Fixing a bug in the list command when submitting an empty string for namespace.

### 1.0.12
- Fixing the help text for the --manual flag. It was wrong and doesn't properly capture what migrate --manual can do.

### 1.0.11
- Fixing bug where optional descriptions weren't actually _optional_ when adding through the sync command.

### 1.0.10
- Adding --skip-upgrade flag
- Fixing a bug with delete where sometimes you could get a success message when a delete failed due to permissions
- Various improvements to using `sync` command when using `--replication-only` flag.
   - Adding prompts to add REPL sources with using sync
   - Notifying of changed configs being UPDATED
   - Adding "orphaned" config notifications.

### 1.0.9
- Improving clarity and format of --info command output.
- A few enhancements to reduce load times on various commands by preventing redundant SSM api calls.
- Improved error handling around `put`. Putting a name with no path would result in stacktrace.
- Fixing a bug in delete, with auto-completed recommendations being removed, even when the delete was blocked.
- Fixing a bug in put where the parameter you just added wouldn't show up in auto-complete if you continued to add more.
- Fixing a bug in browse whereby you were able to circumvent delete validation of replication configs with deleting directories of configs

### 1.0.8
- Fixing a bug with dump command when dumping more than 10 records.
- Adding automated tests that can be run locally (later to be run during automated build process)

### 1.0.7
- Fixing a bug introduced in 1.0.6 with the `cleanup` command.

### 1.0.6
- Adding delete & delete directory functionality to `browse` with the `figgy`
- Fixing a bug with displaying directories in browse with overlapping name prefixes
- Added a `dump` command to allow dumping of configs in JSON
- Added an `audit` command to allow auditing of changes to various parameters.
- Cleaned up --info text across a few commands

### 1.0.5
- Improved validation in `delete` command (won't blow up with empty string, etc)
- Added `sync` with --replication-only to only sync / validate replication configurations (useful for DBAs)
- Major refactoring of how we initialize & leverage parseargs. Moving some redundant code into configuration instead.
- Added this CHANGELOG :D
