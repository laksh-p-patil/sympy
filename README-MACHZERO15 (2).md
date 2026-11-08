# SymPy – Hadamard Product Fixes

**Team Nanosoft | Mach Zero Hackathon**

## About

[SymPy](https://github.com/sympy/sympy) is an open-source Python library for symbolic mathematics. It supports algebra, calculus, equations, and matrix operations.

Our contribution focuses on two issues involving **Hadamard products** in SymPy's matrix and array expression system.

A Hadamard product is simply element-wise matrix multiplication, where corresponding elements of two matrices are multiplied instead of using the usual row-by-column multiplication.

## Fix 1: Incorrect Hadamard Product Orientation

**File:** `from_array_to_matrix.py`

### Problem
When converting array expressions back into matrix expressions, SymPy could sometimes determine the wrong orientation of matrix factors.

This happened because contraction and diagonal indices could become indistinguishable during sorting, causing incorrect ordering.

### Solution
Updated the orientation check to distinguish between the two types of indices before sorting. This prevents index collisions and helps preserve the correct matrix orientation.

### Tests added
- Hadamard product round-trip conversions.
- Transposed factors and longer product chains.
- Non-square matrices, vectors, and traces.
- A derivative test involving Hadamard products.

## Fix 2: Hadamard Product Derivative Error

**Related issue:** #30902, Item 15

### Problem
SymPy had a special derivative handler for Hadamard products that only raised `NotImplementedError`. This prevented the general `MatrixExpr` derivative handler, which could already handle the operation, from being used.

### Solution
Removed the unnecessary special handler and its unused import. SymPy can now use the existing general handler instead of stopping with an error.

### Tests added
- Direct differentiation of Hadamard products.
- Nested products and repeated matrix factors.
- Hadamard products inside determinants, inverses, and matrix powers.
- Non-square matrices, vectors, and symbolic dimensions.
- Comparison against entry-by-entry differentiation.

## Running the Tests

Run these commands from the SymPy repository root.

**Fix 1:**
```bash
pytest sympy/tensor/array/expressions/tests/test_convert_array_to_matrix.py -k orientation_roundtrip
pytest sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py -k trace_hadamard
```

**Fix 2:**
```bash
pytest -q sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py -k hadamard
pytest -q sympy/matrices/expressions/tests/test_derivatives.py -k hadamard
```

## Testing

The development testing recorded:
- New regression tests failing before the derivative fix and passing afterwards.
- Symbolic results matching entry-by-entry differentiation.
- 1,092 existing tensor and matrix tests passing.
- Style and documentation checks passing.

## Scope

These are two separate fixes addressing different problems in SymPy:

1. Correcting Hadamard product orientation during array-to-matrix conversion.
2. Allowing Hadamard products to use the existing matrix-expression derivative handler.

The second fix addresses Item 15 of issue [#30902](https://github.com/sympy/sympy/issues/30902). Neither fix claims to resolve the entire issue.

**Contributed by Team Nanosoft as part of Mach Zero Hackathon.**