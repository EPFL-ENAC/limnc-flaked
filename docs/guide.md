# Guide

## Installation

Development version:

```bash
pip install git+https://github.com/EPFL-ENAC/limnc-flaked.git
```

Released version:

```bash
pip install git+https://github.com/EPFL-ENAC/limnc-flaked.git@1.0.0
```

## Usage

Manual start, see arguments:

```bash
flaked --help
```

Windows deployment, use [nssm](https://nssm.cc/) to make a Service:

```bash
# Windows preliminary:
# * install git
# * install python3
# * install nssm
nssm install Flaked <path-to-flaked.exe>
```

## Configuration

The configuration file is a YAML file, named `config.yml`.

```yaml
# Configuration file for Flaked
settings:
  sftp:
    host: sftp.datalakes.org
    port: 22
    prefix: data
    username: test
    password: test
  logs:
    path: logs
  input: work/instruments
  output: work/backup
instruments:
  - name: instrument1
    schedule:
      cron: "0 0 * * *" # every day at midnight
      interval:
        value: 1
        unit: minutes
    preprocess:
      command: "ls"
      args: ["-la"]
    input:
      path: instrument1/data
      filter:
        skip: 1
    output:
      path: instrument1
  - name: instrument2
    schedule:
      cron: "0 0 * * *" # every day at midnight
      interval:
        value: 1
        unit: minutes
    input:
      path: instrument2/data
      filter:
        regex: ".*\\.csv"
    output:
      path: instrument2
    logs:
      path: logs/instrument2
      level: DEBUG
```