# Local Setup Troubleshooting

## Error: requirements.txt not found

If you see:

```text
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

You are not inside the FlexAI repository folder.

Correct flow:

```bash
git clone https://github.com/Khalidis2/flexai.git
cd flexai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m pytest
```

## Error: not a Python project

If you see:

```text
ERROR: file:///Users/khaled does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found.
```

You ran:

```bash
pip install -e .
```

from the wrong folder.

Run:

```bash
cd ~/flexai
pip install -e .
```

## Check current folder

Run:

```bash
pwd
ls
```

You should see files like:

```text
README.md
requirements.txt
pyproject.toml
flexai/
tests/
tools/
```

If you do not see those files, you are not in the project folder.
