Without the Hand plugged in:

```
python calibration.py --demo
```

With the Hand plugged in:

```
python calibration.py
```

If it crashes, be sure to go and kill all residual python processes (the context manager doesn't nix them, for some undetermined reason).

See "test.py" or "test.m" for examples of extracting/plotting data.
