Sometimes it can be a real pain to deal with building and maintaining URI encoded connection strings. 

Figgy has support for "merge parameters", these parameters allow users to how to merge numerous various configs
into a templated destination config. 

```
      "/app/figgy-demo-merge/replicated/sql/sql-conn-string": [
          "jdbc:mysql://",
          "${/app/figgy-demo-merge/replicated/sql/db/user_name:uri}",
          ":",
          "${/app/figgy-demo-merge/replicated/sql/db/password:uri}",
          "@",
          "${/app/figgy-demo-merge/replicated/sql/db/host:uri}",
          ":",
          "${/app/figgy-demo-merge/replicated/sql/db/port:uri}",
          "/",
          "${/app/figgy-demo-merge/replicated/sql/db/name:uri}"

      ]
    }
```

For instance, in this above example, the parameters in the list will have their values merged
into a single parameter, at the location of `/app/figgy-demo-merge/replicated/sql/sql-conn-string`.

The value of `/app/figgy-demo-merge/replicated/sql/sql-conn-string` would look something like this:

`jdbc:mysql://user:p%40ssw0rd@my-host.com:3306/my_db`

You may append the `:uri` suffix to any merge value to have the value uri-encoded in the result. This is
particularly useful for connection strings :)