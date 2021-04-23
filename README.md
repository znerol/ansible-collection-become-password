# Ansible Collection - znerol.become\_password

Provides an ansible vars plugin which looks up become password using a user
specified command.

## Requirements

* Ansible>=2.10

## Installation

Global installation (recommended):

```bash
ansible-galaxy collection install znerol.become_password
```

Using a `requirements.yml` file:

```yaml
collections:
  - name: znerol.become_password
```

## Configuration

Enable the plugin in `ansible.cfg`:

```ini
[defaults]
vars_plugins_enabled=host_group_vars,znerol.become_password.command
```

The lookup command is specified in `ansible.cfg` as well:

```ini
[znerol.become_password.command]
host_command=/home/me/bin/lookup_sudo_host_password.sh
group_command=/home/me/bin/lookup_sudo_group_password.sh
stage=inventory
```

Note that the command specified using `host_command` or `group_command` ini
settings is invoked without a shell. Hence, it is treated as a path (either
absolute or relative).

The first argument to the command is the inventory hostname or group name.

## Example password lookup script

```
#!/bin/sh
#
# Script template to lookup passwords from some password manager. Uncomment
# whatever works best on your controller machine.

set -eu

INVENTORY_HOSTNAME="${1}"

# # Pass - the standard unix password manager
# # https://www.passwordstore.org/
# #
# # Debian/Ubuntu:
# #
# # apt install pass
# #
# # Docs:
# #
# # man pass
# #
# PASSWORD_STORE_DIR=/home/me/private/my-org-password-store
# /usr/bin/pass "some/subpath/${INVENTORY_HOSTNAME}/become-password"
```

## License

* [GPL-3 or later](https://www.gnu.org/licenses/gpl-3.0.en.html)
