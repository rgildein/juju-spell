# LOGGING

## logging

### JujuSpell commands

Each command has `self.logger` as part of the class and should be used to create logs.

The default format of logging message is:
`%(name)s: %(message)s`
where `name` is name of JujuSpell command.

Recommended format of message is
`%(controller.uuid)s %(message)s`
so logs can be easily filtered.
