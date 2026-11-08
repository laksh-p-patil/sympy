import math
from sympy import symbols, sin, Rational, Expr

x, y = symbols('x y')

cases = [
    ("1. Symbol: math.floor(x)",            lambda: math.floor(x)),
    ("2. Symbol: math.ceil(x)",             lambda: math.ceil(x)),
    ("3. Compound: math.floor(x + y)",      lambda: math.floor(x + y)),
    ("4. Function: math.ceil(sin(x))",      lambda: math.ceil(sin(x))),
    ("5. Fractional: math.floor(x + 1/2)",  lambda: math.floor(x + Rational(1, 2))),
]

def run(title, show_error):
    print("=" * 60); print(title); print("=" * 60)
    for label, action in cases:
        try:
            print(f"[+] {label}\n    RESULT: {action()}\n")
        except TypeError as e:
            print(f"[-] {label}\n    CRASHED WITH TypeError: {e}\n")

# Keep the REAL methods from expr.py (our fix), not a re-written lambda.
real_floor = Expr.__dict__.get('__floor__')
real_ceil = Expr.__dict__.get('__ceil__')
assert real_floor and real_ceil, "Run this on the branch that contains the fix."

# PART 1: genuinely remove our fix -> original upstream behaviour
del Expr.__floor__, Expr.__ceil__
run("PART 1: BEFORE FIX (methods removed from Expr)", True)

# PART 2: restore the exact functions defined in expr.py
Expr.__floor__, Expr.__ceil__ = real_floor, real_ceil
run("PART 2: AFTER FIX (real methods from expr.py)", False)
