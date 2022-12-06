# Workflow


```mermaid
flowchart TD

main(__main__ entrypoint)
check-arguments(check arguments with argparse type, fillter here)
juju-status-cli
connect-manager-context-manager(connect-manager context manager)
assignment-iter(iter over clouds and models, runtime filter models)

subgraph cli module
craft-cli
juju-status-cli
end

subgraph fill.py
check-arguments
end

subgraph assignment module
assignment-func
connect-manager-context-manager
assignment-iter
end

subgraph commands module
juju-commands
end

subgraph connections
connect-manager
juju-data
end

main --> craft-cli

craft-cli -.-> check-arguments

check-arguments -.-> craft-cli

craft-cli --> juju-status-cli
juju-status-cli --> assignment-func --> connect-manager-context-manager
connect-manager -.-> connect-manager-context-manager
connect-manager-context-manager--> assignment-iter
assignment-iter --> juju-commands
```


- **__main__ entrypoint**:
    - setup cli and exit
- **fill.py**
    - all filter function will put here
- **cli module**
    - Only include setup cli command & argparse.
- **assignment module**
    - High level business logic.
    - The connection should be handled here.
- **connect manager**
    - JAAS/ssh tunnel/sshuttle connection manager
- **commands module**
    - The command should only consider how to working with the juju controller.
