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

The configuration describes the system settings and a list of instrument descriptions, which specifies how to process the instrument data files. The format of the configuration file is YAML, and the file is named `config.yml`.

Example of configuration file:

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
    input:
      path: instrument2/data
      filter:
        regex: ".*\\.csv"
    output:
      path: instrument2
    logs:
      path: instrument2
      level: DEBUG
```

### Settings

Some general settings.

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `sftp`      | SFTP server settings                |
| `logs`      | Logs settings                       |
| `input`     | Input directory settings, optional  |
| `output`    | Output directory settings, optional |

#### SFTP

How to connect to the SFTP server where the data will be uploaded.


| Key         | Description                         |
| ----------- | ----------------------------------- |
| `host`      | SFTP server hostname                |
| `port`      | SFTP server port, default is `22`   |
| `prefix`    | SFTP server path prefix, e.g. `data`|
| `username`  | SFTP server username                |
| `password`  | SFTP server password                |

#### Logs

Where the logs will be stored, with which level of details.

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `path`      | Logs directory base path: if not absolute, it will be relative to the current working directory. |
| `level`     | Default log level, possible values: `DEBUG`, `INFO`, `WARNING`.                                  |

#### Input

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `path`      | Input directory path prefix, used if the input directory of an instrument is relative. |

#### Output

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `path`      | Output directory path prefix, used if the input directory of an instrument is relative. |

### Instruments

An array of instrument descriptors, that define which and how data are to be handled, at which frequency. 

#### Instrument

| Key           | Description                         |
| ------------- | ----------------------------------- |
| `name`        | Instrument name, must be unique.                                         |
| `schedule`    | When the input data file must be processed.                              |
| `preprocess`  | Preprocessing command to execute before handling input files, optional.  |
| `postprocess` | Postprocessing command to execute after handling output files, optional. |
| `input`       | Input data files selector. |
| `output`      | Output folder where input files will be moved. |
| `logs`        | Logs  |

##### Schedule

There are two kinds of scheduling:
- `cron`: complex scheduling expression
- `interval`: regular intervals of unit of time

One or the other, or both, can be defined for an instrument. The corresponding scheduler job identifier will be postfixed by `:cron` or `:interval`respectively.

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `cron`      | Cron expression |
| `interval.value`  | Interval integer value. |
| `interval.unit`   | Interval unit, possible values are: `minutes`, `hours`, `days`, `weeks` |

##### Preprocess

A pre-processing directive consists of executing a command, before the input files are handled, with optional arguments.

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `command`   | Path to the command to execute.      |
| `args`      | Array of command arguments, optional |

##### Postprocess

A post-processing directive consists of executing a command, after the output files were handled, with optional arguments.

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `command`   | Path to the command to execute.      |
| `args`      | Array of command arguments, optional |

##### Input

Where are located the input data fiels and how to select them.

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `path`      | Iutput directory path: if not absolute, it will be relative to the main input directory (if defined) or to the current working directory. |
| `filter.skip`  | The number of files to skip, counting from the latest ones.        |
| `filter.regex` | A regular expression pattern which file name must match, optional. |

##### Output

In which directory are moved the processed input files.

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `path`      | Output directory path               |

##### Logs

Where the logs of the instrument's data processing will be stored, with which level of details. Note that the ouput of the pre/post-processing commands are included in this log.

| Key         | Description                         |
| ----------- | ----------------------------------- |
| `path`      | Logs directory base path: if not absolute, it will be relative to the main logs directory (if defined) or to the current working directory. |
| `level`     | Default log level, possible values: `DEBUG`, `INFO`, `WARNING`. |

The format of the log file is CSV (without header) with the columns:

- `timestamp`: datetime of the log entry
- `level`: the log level of the log entry
- `instrument`: the instrument name
- `action`: the type of action that produced the log entry
- `message`: the human readable message
- `arguments`: some informative metrics, optional

## API

Flaked is a process that runs in the background. It exposes a REST API so that one can query the current status of the service, and can modify the configuration.

The interactive documentation of the REST API is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Scheduler status

It is possible to start/stop or pause/resume the scheduler.

### Instrument jobs

For each instrument scheduling directive (`cron` or `interval`) ther is a job. Each of this job has the following properties:

| Key             | Description                         |
| --------------- | ----------------------------------- |
| `id`            | The job unique identifier, is based on the corresponding instrument's name, postfixed by the scheduling type. |
| `name`          | The name of the corresponding instrument.                                                   |
| `trigger`       | The trigger directive, either an interval in seconds or the details of the cron expression. |
| `next_run_time` | When will be the next execution. When the job is paused, there is none.                     |

It is possible to start/stop or pause/resume a job in the scheduler. Stopping removes the job from the scheduler, restarting it recreates the job according to the instrument specifications. Pausing a job postpones its next execution. Resuming it recalculates the next run time according to the job trigger definition.