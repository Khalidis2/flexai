# Python Versions

FlexAI currently targets:

```text
Python 3.11 or Python 3.12
```

Python 3.14 is not recommended yet. Some geometry and scientific dependencies may not publish stable wheels for the newest Python release immediately.

## Recommended macOS setup

Install Python 3.12 with Homebrew:

```bash
brew install python@3.12
```

Then create the virtual environment from inside the FlexAI repository:

```bash
cd ~/flexai
rm -rf .venv
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
```

On Intel Macs, Homebrew may install Python at:

```bash
/usr/local/bin/python3.12
```

Check with:

```bash
which python3.12
python3.12 --version
```

After activating the environment, confirm:

```bash
python --version
```

Expected:

```text
Python 3.12.x
```
