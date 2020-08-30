
I suspect this was originally intended to run under Python 3.6, but later versions should work? (or I don't have any a priori reason to think they wouldn't).

First, we'll make a virtual environment:

```
python -m venv env
env\Scripts\activate # on Windows, source env/bin/activate on Unix
pip install -r requirements.txt
deactivate
```

Whenever you want to run the script, make sure the environment is activated (see above).

To test without the Hand plugged in:

```
python calibration.py --demo
```

With the Hand plugged in:

```
python calibration.py
```

If it crashes, be sure to go and kill all residual python processes (the context manager doesn't nix them, for some undetermined reason).

See "test.py" or "test.m" for examples of extracting/plotting data.
