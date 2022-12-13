# Workflow


```mermaid
flowchart TD

main(__main__ entrypoint)
check-arguments(check arguments with argparse type, load config and filter controllers)
status-cli

subgraph cli module
craft-cli
status-cli
end

subgraph filler
check-arguments
end

subgraph assignment module
assignment-run-func
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

craft-cli --> status-cli

subgraph assignment-run-func

run-serial
run-batch
run-parallel
end

status-cli --run-async--> assignment-run-func
connect-manager -.-> assignment-run-func

assignment-run-func --> juju-commands
```


- **__main__ entrypoint**:
    - setup cli and exit
- **filter**
    - all filter function will put here
- **cli module**
    - Only include setup cli command, add argparse, and format output.
- **assignment module**
    - High level business logic.
    - The connection should be handled here.
    - Provides different assignment functions to run e.g., batch, serial and parallel.
- **connect manager**
    - JAAS/ssh tunnel/sshuttle connection manager
- **commands module**
    - The command should only consider how to working with the juju controller.
