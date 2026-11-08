# SymPy: Hadamard Product and Array Expression Fixes

**Team Nanosoft | Mach Zero Hackathon**

## Overview

This contribution addresses two independent issues in SymPy's matrix and array expression system involving Hadamard products.

[SymPy](https://github.com/sympy/sympy) is an open-source Python library for symbolic mathematics. It supports algebraic expressions, calculus, equation solving, matrix operations, and symbolic differentiation.

A **Hadamard product** is an element-wise matrix multiplication operation. Unlike conventional matrix multiplication, it multiplies corresponding entries of two matrices.

For example:

\[
\begin{bmatrix}1&2\\3&4\end{bmatrix}
\odot
\begin{bmatrix}5&6\\7&8\end{bmatrix}
=
\begin{bmatrix}5&12\\21&32\end{bmatrix}
\]

This contribution focuses on ensuring that SymPy correctly handles Hadamard products during expression conversion and symbolic differentiation.

---

## Fix 1: Correct Hadamard Product Orientation During Array-to-Matrix Conversion

**File:** `sympy/tensor/array/expressions/from_array_to_matrix.py`

### Problem

SymPy could incorrectly determine the orientation of matrix factors when converting array expressions back into matrix expressions.

The underlying issue was related to how two types of indices were represented:

- Contraction indices are non-negative integers (`>= 0`).
- Diagonal indices are represented as `-1-i`.

The previous implementation converted diagonal indices back into non-negative values before comparing their ordering. When both types appeared in the same group, distinct indices could collide. For example, `0` and `-1` could both become `0`.

This could make an incorrectly ordered group appear sorted, resulting in an incorrect matrix orientation.

### Solution

The orientation check in `identify_hadamard_products()` was updated.

When a group contains both contraction and diagonal indices, indices are now represented using the tuple `(i < 0, i)` before sorting.

This ensures that:
- Contraction indices are ordered before diagonal indices.
- Distinct index representations remain distinguishable.
- Groups containing only one index type retain their previous behaviour.

### Tests Added

**1. Hadamard product round-trip tests**

File: `test_convert_array_to_matrix.py`

The new tests cover:
- Transposed matrix factors.
- Longer Hadamard product chains.
- Non-square matrices and vectors.
- Trace expressions.
- Preservation of explicit matrix values.
- Consistency when conversions are performed repeatedly (idempotency).

**2. Derivative regression test**

File: `test_arrayexpr_derivatives.py`

Tests the derivative of a trace expression involving Hadamard products and verifies the symbolic result against an independently computed explicit-array derivative.

---

## Fix 2: Enable Array Derivatives of Hadamard Products

**Related issue:** [SymPy #30902 — Item 15](https://github.com/sympy/sympy/issues/30902)

### Problem

SymPy previously had a specialised `array_derive` handler for `HadamardProduct`.

However, this handler only raised `NotImplementedError`.

SymPy also had a general derivative handler for `MatrixExpr` that could already handle the operation.

Because SymPy's dispatch mechanism selects the most specific available handler, the specialised handler was always selected instead of the working general handler.

As a result, certain array differentiation operations involving Hadamard products failed.

### Solution

Instead of introducing another derivative implementation, the unused specialised handler was removed.

The `HadamardProduct` registration and its now-unnecessary import were deleted from:

` sympy/tensor/array/expressions/arrayexpr_derivatives.py `

This allows SymPy's existing general `MatrixExpr` handler to process Hadamard products.

The existing general implementation is reused, avoiding duplicated derivative logic.

### Tests Added

The regression tests cover:

**1. Dispatch behaviour**
- Verifies that Hadamard products use the general `MatrixExpr` derivative handler.
- Checks the resulting derivative and its expected shape.

**2. Numerical differentiation**
- Compares symbolic derivatives against an entry-by-entry reference using `derive_by_array`.
- Covers repeated factors, nested Hadamard products, transposes, traces, and matrix expressions.

**3. Nested matrix operations**
- Tests Hadamard products inside determinants, inverses, and matrix powers, including positive and negative integer powers.

**4. Edge cases**
- Variables absent from the expression.
- Non-square matrices.
- Row and column vectors.
- Scalar-sized matrices.
- Symbolic dimensions.
- Expressions that cannot be converted by the general handler.

**5. Matrix function differentiation**

Additional tests verify differentiation of determinants, inverses, matrix powers, and traces involving Hadamard products.

---

## Running the Tests

Run the following commands from the SymPy repository root.

### Fix 1: Orientation and round-trip tests

```bash
pytest sympy/tensor/array/expressions/tests/test_convert_array_to_matrix.py -k orientation_roundtrip
```

### Fix 1: Trace derivative test

```bash
pytest sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py -k trace_hadamard
```

### Fix 2: Array derivative tests

```bash
pytest -q sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py -k hadamard
```

### Fix 2: Matrix derivative tests

```bash
pytest -q sympy/matrices/expressions/tests/test_derivatives.py -k hadamard
```

---

## Verification Results

The development testing recorded the following results:

- Regression tests reproduced the original derivative failure before the second fix.
- The new tests passed after the fallback handler was enabled.
- Symbolic differentiation results matched the independent entry-by-entry reference calculations.
- Edge cases, including non-square matrices and symbolic dimensions, were tested.
- 1,092 existing tests across the tensor and matrix code passed.
- Style and documentation checks passed.

The saved before-and-after demonstration outputs document the observed behaviour.

---

## Scope of Contribution

These are two separate fixes addressing different problems:

| Fix | Area | Objective |
|---|---|---|
| Fix 1 | Array-to-matrix conversion | Correct Hadamard product orientation |
| Fix 2 | Array differentiation | Enable the existing general derivative fallback |

The second fix addresses **item 15 of issue #30902**. These changes do not claim to resolve all 35 defects listed in that issue.

## Acknowledgements

This work was contributed by **Team Nanosoft** as part of the **Mach Zero Hackathon**, with the aim of improving the correctness and reliability of SymPy's symbolic matrix and array operations.

Repository: https://github.com/sympy/sympy