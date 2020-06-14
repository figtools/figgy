The `shared_figs` block is how you define parameters that must existing your application's namespace but 
you don't have control over. 

For instance, suppose you need a DB Password and DB user but you don't have access to that user or password? You can 
ask other figgy users, like your DBA, to share the password with your application.

In this example the user is defining in her config that she MUST have these parameters available in parameter store for
her application to run.

`/app/figgy-demo-shared/db/user`
`/app/figgy-demo-shared/db/password`

During build-time figgy can validate those parameters properly exist and save you from a failed deployment!

Our DBA in this situation who owns these configs, can share these secrets directly with your application code with the
`figgy config share` command or `figgy config sync --replication-only` commands. 

**You don't need the secret, your code does** Protect yourself, have secret owners share their secrets with your code
directly! :)
