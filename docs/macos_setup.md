# macOS Setup

Some macOS systems do not provide the `python` or `pip` commands by default.

Use `python3` instead.

## Correct setup

From inside the FlexAI repository:

```bash
cd ~/flexai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
```

After activating the virtual environment, `python` should work because it points to `.venv/bin/python`.

## If python3 is missing

Install Python from one of these options:

### Option A: Homebrew

```bash
brew install python
```

### Option B: Official Python installer

Download Python for macOS from python.org.

## Check commands

```bash
which python3
python3 --version
```

After activating the virtual environment:

```bash
which python
python --version
which pip
pip --version
```
