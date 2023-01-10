# JujuSpell

juju-spell snap controls all clouds in a centralized way

## Purpose

JujuSpell is a CLI tool to communicate with multiple juju controllers that may behind the jump server.

It will allow user:

- Run juju command to multiple remote controllers
- Implement a complex steps of operation command like building a block(juju command) with *python-libjuju*.
- Friendly CLI interface that allow user to config/filter/confirm with the arguments.

The tool has two major parts: *connection* and *assignment*.
Connection is the handler to connect to remote controller. Assignment is the mechanism about how to run multiple juju command on multiple juju controllers.

The details of design please read [architecture.md](./docs/architecture.md)

## Installation

To get the latest stable version of the snap from Snapstore, run:

```bash
sudo snap install juju-spell
```

To get the latest development version of the snap, build from the source code and install with `--dangerous` flag:

```bash
make build
sudo snap install --dangerous juju-spell.snap
```
