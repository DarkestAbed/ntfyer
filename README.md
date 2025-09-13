![](.github/assets/logo.png)

# ntfyer

### A small and effective `ntfy.sh` wrapper utility

### Features

- Configure to use any [ntfy.sh](https://ntfy.sh/) server
    - Even private instances!
- Send notifications to your notification service
- Easily integrate into your Linux CLI workflow

## Install

```
Dependencies:

- python >= 3.13
- pipx

Installation:

> pipx install git+https://github.com/DarkestAbed/ntfyer
```

### Known issues

- Your `pipx` installation may fail without a clear log. If this happens, you might want to try
```bash
pipx install git+https://github.com/DarkestAbed/ntfyer --python $(which python)
```
- If you are not getting notifications, review the notification server and topic using
```bash
ntfyer config get
```

## Command Line Interface use

```
Basic CLI usage:
    ntfyer send <TEXT>                  : sends TEXT as a notification to the previously configured ntfy.sh instance

Other commands:
    ntfyer config get                   : Outputs the current ntfy.sh instance URL
    ntfyer config url <URL>             : Sets the URL (without topic) of the ntfy.sh instance
    ntfyer config topic <TOPIC>         : Sets the topic of the ntfy.sh instance to message
```

## Contributing

Please open an Issue or a PR if you want to contribute to the project.

This project is released under GPL-3. Please consider and comply with GPL-3 License requirements.

## Changelog

Please refer to [CHANGELOG](CHANGELOG.md)
