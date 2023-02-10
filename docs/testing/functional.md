# Functional tests

## How to run

Running functional tests without any configuration.

```bash
tox -e func
```

Running functional tests without building snap. This is only ment to be used during development of functional tests, so when no changes in JujuSpell was made.

```bash
tox -e -- --bo-build
```

To not clean up the testing environment after successful / unsuccessful tests.

```bash
tox -e -- --keep-env
```

## Environment

Test environment is created on top of LXD, where 3 containers will be created. The first container is representing a client, which does not have direct access to any of the following controllers. Next two containers are bootstrapped controllers.

The `--series <desired-series>` option can be used to change the series used to create client and bootstrapped controllers. The default value is `jammy`.

![LXD environemnt](./env.svg?raw=true "LXD environment")

### The client

This container is created and configured in such way, that it could not directly reached any of controllers. This is accomplished with firewall rule as follows.

```bash
ufw deny out <port-configured-during-bootstrapping>
```

The JujuSpell snap is copied and installed with `--devmode`.

In order to enable ssh with any controller, an ssh key is generated, which is then added to as authorized-keys for each controller.

The last step is to generate the configuration file for JujuSpell where the IP of the controller container is used for the `connection.destination`. This part is needed to connect to the controller, because direct access is blocked by the firewall.

### Controllers

There is nothing special about controllers, each of them are under the same LXD cloud and they are using a series specified with `--series`.

The only non-standard is that they don't use the default port `17070`, but a port defined as a constant (`CONTROLLER_API_PORT`) in the code.
