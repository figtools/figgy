 
## How to deploy:
To deploy the figgy you'll want to make sure ALL of your changes are checked in, and that the config.py VERSION has been incremented.

So suppose the current deployed version is '1.0.0'

To deploy a new version you would update config.py VERSION to '1.0.1'

You would then COMMIT that change to master, and wait for all 3 builds to finish for linux / darwin / windows.

Next export credentials to mgmt `figgy iam export --env  mgmt`

Finally you will need to run ./deploy.sh which will deploy your new version of 1.0.1 and will trigger auto-upgrades for user.
