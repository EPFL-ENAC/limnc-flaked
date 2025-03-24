# Installation

## From Github

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
