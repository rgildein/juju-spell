# JujuSpell

juju-spell snap controls all clouds in a centralized way

## Deployment

To get the latest stable version of the snap from Snapstore, run:

```bash
sudo snap install juju-spell
```

To get the latest development version of the snap, build from the source code and install with `--dangerous` flag:

```bash
make build
sudo snap install --dangerous juju-spell.snap
```
## Config

The config for juju-spell continues list of controllers where each controller have fallowing attributes:

* `name` controller name (both on the client side and in the controller)
* `customer` customer name for better identification
* `owner` owner name
* `description` [optional] controller description
* `tags` [optional] list of tags used for filtering
* `risk` [optional] risk level [1-5] used for filtering, where 5 is default value and the most risky
* `endpoint` controller api endpoint (currently we are not supporting multiple api endpoints)
* `ca_cert` certificate for controller
* `username` username
* `password` password
* `model_mapping` {lma, default} map model category to real name of the model
* `connection` [optional] definition for remote clouds (sshuttle and port-forwarding)
  * `destination` remote destination accessible with ssh
  * `subnets` [optional] list of subnets, this option will be used with sshuttle enabled
  * `jumps` [optional] ssh jumps are sorted according to the order in which they are performed


Example:
```yaml
controllers:
  - name: example_controller
    customer: example_customer
    owner: Gandalf
    description: some nice notes about controllers and models  # optional
    tags: ["test"]  # optional
    risk: 5  # optional [5]
    endpoint: 10.1.1.46:17070
    ca_cert: |
        -----BEGIN CERTIFICATE-----
        -----END CERTIFICATE-----
    username: admin
    password: pass1234
    model_mapping:
      lma: monitoring
      default: production
    connection:  # optional
      destination: ubuntu@10.1.1.99  # infra node
      subnets:  # optional (sshuttle)
        - 10.1.1.0/24
        - 20.1.1.0/24
      jumps:  # optional
        - bastion
```
