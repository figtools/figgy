Config replication enables the continued synchronization of configurations between a single source and N destinations.

In this example the user has defined they want source -> destination replication to occur for these values:
 
`/shared/service-map/foo/hostname` -> `/app/figgy-demo-repl/foo.hostname`
`/shared/service-map/foo/port` -> `/app/figgy-demo-repl/foo.port`

By running the `figgy config sync` command against this figgy-replication.json file, figgy will configure continuous
event-driven synchronization between these sources and destinations. 

For example, if someone updates the value of: `/shared/service-map/foo/hostname`, the destination value will
be automagically updated within approximately 1 second. 

In this example the _source_ of replicatoin is under the `/shared` namespace. The `/shared` namespace is for global
non-secret configurations. They can be _shared_ into other application namespaces via replication. Figgy handles
the synchronization for you. 

Define what you want and let `figgy` do the rest. 