# Installation

## From Github

Windows preliminary:

* install [python3](https://www.python.org/) with 'Customize installation': 'Install for all users' and 'Add Python to environment variables' checked
* install [git](https://git-scm.com/)
* install [nssm](https://nssm.cc/)

Development version:

```bash
pip install git+https://github.com/EPFL-ENAC/limnc-flaked.git
```

Released version:

```bash
pip install git+https://github.com/EPFL-ENAC/limnc-flaked.git@1.0.0
```

On Windows, register the service:

```bash
nssm install Flaked <path-to-flaked.exe>
```

## Usage

Manual start, see arguments:

```bash
flaked --help
```

Or as a Windows service, use nssm:

```bash
nssm start Flaked
```

## Upgrade

Make sure to stop the Windows service before upgrading and restart it after:

```bash
nssm stop Flaked
pip install git+https://github.com/EPFL-ENAC/limnc-flaked.git@1.1.0
nssm start Flaked
```

## Troubleshooting

Check nssm status:

```bash
nssm status Flaked
```

Edit nssm configuration:

```bash
nssm edit Flaked
```

Verify server API is accessible at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).