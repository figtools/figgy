In this example we are defining how to specify what  applicatin-specific parameters your application _needs_ to run.

If you run `figgy config sync --config figgy-simple.json` you will be prompted to enter these parameters. Any
missing parameters can be detected at build-time validation using `figgy config validate`. 

```{
    "namespace": "/app/figgy-demo-simple",
    "app_parameters": [
      "api_key",
      "logging/level",
      "logging/format"
    ]
}
```

This block defines that the following parameters are required for application `figgy-demo-simple`

`/app/figgy-demo-simple/api_key`
`/app/figgy-demo-simple/logging/level`
`/app/figgy-demo-simple/logging/format`

The `sync` command will check to ensure these exist for the specified environment and will prompt you to add
any missing parameters or notify you of parameters that are in ParameterStore but are missing from your definition here.