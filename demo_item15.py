"""Demo for SymPy issue #30902, item 15.  Run from the sympy repo root:
    PYTHONPATH=. python3 /home/claude/demo_item15.py
Run it once on the ORIGINAL code and once on the FIXED code."""
from sympy import (MatrixSymbol, HadamardProduct, Determinant, Inverse,
                   ImmutableMatrix, symbols, derive_by_array, Array)
from sympy.tensor.array.expressions.arrayexpr_derivatives import array_derive

def banner(t):
    print("\n" + "=" * 70 + "\n" + t + "\n" + "=" * 70)

def numeric_check(expr, var, repl, numrepl=None):
    """Compare SymPy's answer with the slow-but-trusted answer
    (differentiate every single matrix entry one by one)."""
    numrepl = numrepl or {}
    got = array_derive(expr, var).as_explicit().subs(repl).doit().subs(numrepl)
    ground = expr.subs(repl).doit()
    expected = derive_by_array(ground, repl[var]).subs(numrepl)
    diff = (Array(got) - Array(expected)).applyfunc(lambda t: t.doit().simplify())
    return diff == Array.zeros(*expected.shape)

def attempt(label, fn):
    try:
        out = fn()
        print(f"  {label}: WORKS")
        return out
    except NotImplementedError as e:
        print(f"  {label}: CRASH -> NotImplementedError")
    except Exception as e:
        print(f"  {label}: CRASH -> {type(e).__name__}: {e}")

M = MatrixSymbol("M", 2, 2)
N = MatrixSymbol("N", 2, 2)
H = HadamardProduct(M, N)               # "M times N, entry by entry"
m, n = symbols("m:4"), symbols("n:4")
repl = {M: ImmutableMatrix(2, 2, m), N: ImmutableMatrix(2, 2, n)}
numrepl = dict(zip(m + n, [3, 1, 2, 5, 2, 1, 1, 3]))

banner("PART 1 - THE ORIGINAL ERROR\n"
       "Ask SymPy: how does (M x N, entry by entry) change when M changes?")
attempt("derivative of H with respect to M", lambda: array_derive(H, M))
attempt("derivative of Determinant(H)     ", lambda: array_derive(Determinant(H), M))
attempt("derivative of Inverse(H)         ", lambda: array_derive(Inverse(H), M))

banner("PART 2 - WORKING TEST CASE\n"
       "Does SymPy's answer match the slow trusted answer? (True = correct)")
for name, e in [("H", H), ("Determinant(H)", Determinant(H)), ("Inverse(H)", Inverse(H))]:
    try:
        print(f"  {name:16s}: matches trusted answer = {numeric_check(e, M, repl, numrepl)}")
    except NotImplementedError:
        print(f"  {name:16s}: CRASH -> NotImplementedError (could not even check)")

banner("PART 3 - EDGE CASES (unusual inputs)")
P, Q = MatrixSymbol("P", 2, 3), MatrixSymbol("Q", 2, 3)
r2 = {P: ImmutableMatrix(2, 3, symbols("p:6")), Q: ImmutableMatrix(2, 3, symbols("q:6"))}
cases = [
    ("non-square matrices (2x3)       ", lambda: numeric_check(HadamardProduct(P, Q), P, r2)),
    ("same matrix twice, M with M     ", lambda: numeric_check(HadamardProduct(M, M), M, repl)),
    ("variable not in the expression  ", lambda: array_derive(H, MatrixSymbol("Z", 2, 2)).shape == (2, 2, 2, 2)),
]
for label, f in cases:
    try:
        print(f"  {label}: correct = {f()}")
    except NotImplementedError:
        print(f"  {label}: CRASH -> NotImplementedError")
print()
