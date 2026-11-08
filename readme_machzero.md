# README-MACHZERO.md: Project MachZero Engineering Log

## Team & Project Overview
- **Target Repository:** [sympy/sympy](https://github.com/sympy/sympy)
- **Target Issue:** [Issue #5916: Make sure all the built-in __methods__ are defined](https://github.com/sympy/sympy/issues/5916)
- **Primary Milestone:** Implement standard library arithmetic/truncation protocol methods (`__floor__` and `__ceil__`) on `Expr`.
- **Target Branch:** `expr-floor-ceil`

---

## 1. Round 1: Repository & Issue Selection Journey

### Repository Selection
We selected **SymPy** (`sympy/sympy`), the core computer algebra system for Python. SymPy is foundational to the scientific Python ecosystem (SciPy, SageMath, Astropy). Contributing to its core expression engine (`sympy.core`) delivers immediate, high-leverage impact to scientific computing and symbolic manipulation.

### Issue Discovery, Exploration 
During Round 1, our primary constraint was identifying a meaningful, open issue authored by a core maintainer with **zero existing solutions or open PRs**, solvable within our hackathon timeline without introducing breaking changes.



## 2. Selected Issue: #5916 (`Make sure all the built-in __methods__ are defined`)

### Author & Validation
- **Author:** Aaron Meurer (`@asmeurer`, former SymPy project lead / core maintainer).
- **Labels:** `core`, `Easy to Fix`, `Bug`.
- **Current GitHub State:** Verified Open, with **No branches or pull requests** linked under the Development section.


---

## 3. Technical Architecture & Root Cause Analysis

### The Problem
When users pass a SymPy symbolic expression or symbol to Python's standard `math` library:
```python
import math
from sympy import Symbol
x = Symbol('x')
math.floor(x)
```
Python checks for the `__floor__` dunder method on `x`. In SymPy, `__floor__` and `__ceil__` were implemented on `Number` (`sympy.core.numbers`), but **omitted on `Expr`** (`sympy.core.expr`). Consequently, Python falls back to `float(x)`, which raises:
```text
TypeError: Cannot convert expression to float
```

### The Solution
Implement `__floor__` and `__ceil__` directly on `sympy.core.expr.Expr`, delegating directly to SymPy's symbolic `floor(self)` and `ceiling(self)` functions. This ensures:
1. `math.floor(Symbol('x'))` returns `floor(x)`.
2. `math.ceil(Symbol('x'))` returns `ceiling(x)`.
3. Evaluatable constants and exact expressions (e.g. `math.floor(pi)`, `math.ceil(Rational(7, 2))`) evaluate directly to exact integers.
4. Seamless compatibility with Python's standard library `math` module.

---

## 4. Implementation Details

### Changes to `sympy/core/expr.py`
Located below `Expr.__abs__`:

```python
    def __abs__(self) -> Expr:
        from sympy.functions.elementary.complexes import Abs
        return Abs(self)

    def __floor__(self) -> Expr:
        from sympy.functions.elementary.integers import floor
        return floor(self)

    def __ceil__(self) -> Expr:
        from sympy.functions.elementary.integers import ceiling
        return ceiling(self)
```

### Unit Tests in `sympy/core/tests/test_expr.py`
Located below `test_trunc()`:

```python
def test_floor_ceil():
    import math
    from sympy.functions.elementary.integers import floor, ceiling
    x, y = symbols('x y')

    # Symbolic variables and composite expressions
    assert math.floor(x) == floor(x)
    assert math.ceil(x) == ceiling(x)
    assert math.floor(x + y) == floor(x + y)
    assert math.ceil(x + y) == ceiling(x + y)

    # Exact numbers and mathematical constants
    assert math.floor(pi) == 3
    assert math.ceil(pi) == 4
    assert math.floor(Rational(7, 2)) == 3
    assert math.ceil(Rational(7, 2)) == 4
    assert math.floor(-Rational(7, 2)) == -4
    assert math.ceil(-Rational(7, 2)) == -3
```

---

## 5. Verification & Test Run Output

```text
============================= test session starts ==============================
collected 1 item

sympy/core/tests/test_expr.py::test_floor_ceil PASSED                    [100%]

============================== 1 passed in 0.18s ===============================
```

---

## 6. Round 2 & Round 3 Deliverables Checklist

- [x] **Repository Selection:** `sympy/sympy` selected and validated.
- [x] **Issue Selection:** Issue #5916 confirmed open, maintainer-authored, zero conflicts.
- [x] **Documentation Artifact:** `README-MACHZERO.md` authored detailing journey, failures, and implementation.
- [ ] **Fork Created:** Lead creates GitHub fork of `sympy/sympy`.
- [ ] **Teammates Added:** All team members invited as collaborators on the fork.
- [ ] **Code Committed:** Changes pushed to feature branch `expr-floor-ceil` on team fork.
- [ ] **PR Ready:** Pull request draft prepared for Round 3 judging.
