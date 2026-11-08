# SymPy – Hadamard Product Derivative Fix

**Team Nanosoft | Mach Zero Hackathon**

## About

[SymPy](https://github.com/sympy/sympy) is an open-source Python library for symbolic mathematics. It supports algebra, calculus, equations and matrix operations.

Our contribution addresses **Item 15 of [SymPy issue #30902](https://github.com/sympy/sympy/issues/30902)**, which involves an error when differentiating Hadamard products.

A Hadamard product is element-wise matrix multiplication, where corresponding elements of two matrices are multiplied instead of using the usual row-by-column multiplication.

## The Problem

**File:** `sympy/tensor/array/expressions/arrayexpr_derivatives.py`

SymPy had a specialised derivative handler for `HadamardProduct` that simply raised `NotImplementedError`.

However, SymPy also had a general derivative handler for `MatrixExpr` that could already handle Hadamard products by converting them into array expressions.

Since SymPy's dispatch system always selects the most specific matching handler, it chose the specialised handler and never reached the general one.

As a result, certain differentiation operations involving Hadamard products failed.

## The Fix

Instead of creating another differentiation implementation, we removed the unnecessary specialised handler and its unused `HadamardProduct` import.

This allows SymPy to use its existing general `MatrixExpr` handler, which converts the expression into an array and performs the differentiation.

This avoids duplicating existing logic and makes use of functionality that was already available.

## Tests Added

The regression tests cover the following cases:

**1. Dispatch behaviour**
- Checks that Hadamard products use the general `MatrixExpr` derivative handler.
- Verifies the derivative result and expected shape `(3, 3, 3, 3)`.

**2. Numerical differentiation**
- Compares SymPy's result against an independent entry-by-entry differentiation method using `derive_by_array`.
- Covers repeated factors, nested Hadamard products, transposes, traces and matrix expressions.

**3. Nested matrix operations**
- Tests Hadamard products inside determinants, inverses and matrix powers.
- Includes both positive and negative integer powers.

**4. Edge cases**
- Variables that do not appear in the expression (expected zero derivative).
- Non-square matrices (2×3).
- Row and column vectors.
- 1×1 matrices.
- Symbolic matrix dimensions.
- Expressions that cannot be converted by the general handler, ensuring they still raise `NotImplementedError` instead of causing an endless loop.

**5. Matrix function differentiation**

Additional tests check differentiation of determinants, inverses, matrix powers and traces involving Hadamard products.

## Running the Tests

Run these commands from the SymPy repository root.

**Array derivative tests:**

```bash
pytest -q sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py -k hadamard
```

**Matrix derivative tests:**

```bash
pytest -q sympy/matrices/expressions/tests/test_derivatives.py -k hadamard
```

## Testing Results

The development testing recorded:

- The original implementation reproduced the `NotImplementedError`.
- Four focused regression tests failed before the fix and passed afterwards.
- Symbolic differentiation results matched the independent entry-by-entry reference calculations.
- Edge cases, including non-square matrices and symbolic dimensions, were tested.
- 1,092 existing tests across the tensor and matrix code passed.
- Style and documentation checks passed.
  
1. **Get the code and the branch:**

   ```bash
   git clone --branch "15-hadamard-fallback(Maitreya)" [https://github.com/laksh-p-patil/sympy](https://github.com/laksh-p-patil/sympy)
   cd sympy
   pip install mpmath pytest

Keep the quotes around the branch name, because of the brackets. The fix, the tests and the demo are already on this branch.

2. If Python later says it “could not determine its version”: GitHub forks don’t copy SymPy’s version tags. Run this once, then retry:

git tag sympy-1.15.dev

3. See the original error. This temporarily puts the original code back:

git checkout 1e60306 -- sympy/tensor/array/expressions/arrayexpr_derivatives.py

$env:PYTHONPATH="."
python item15_submission/demo_item15.py

4. Put the fix back:
git checkout HEAD -- sympy/tensor/array/expressions/arrayexpr_derivatives.py
5. See it working. Run the same demo command as step 3, then:

python -m pytest -v sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py -k hadamard
6. Optional, for the full picture:

python -m pytest -q sympy/tensor sympy/matrices/expressions

## Scope

This contribution addresses **Item 15 of issue #30902**. It does not claim to resolve all 35 defects listed in the issue.

**Contributed by Team Nanosoft | Mach Zero Hackathon**
