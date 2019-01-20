# Flasks

## Setup

1. Install SO requirements
 
 * python3
 * pip >= 10.0.0
 * virtualenv >= 15.1.0

2. Create a virtual environment with virtualenv (outside project directory)
```sh
# It would create a virtualenv virtual environment with 'venv' alias
virtualenv venv -p python3
```

3. Install requirements.txt

```sh
# First, start the 'venv' virtual environment
source venv/bin/activate
# Install requirements.txt
(venv) pip install -r requirements.txt
```
## Start

```sh
# First, start the 'venv' virtual environment
source venv/bin/activate
# Go to project directory, so start the main script
(venv) python main.py
```