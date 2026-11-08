# SymPy #30902: how we did it

Event: Mach Zero, 7-8 Nov 2026
Team: Nanosoft
Fork: https://github.com/laksh-p-patil/sympy
Issue: https://github.com/sympy/sympy/issues/30902

## 1. Choosing the issue

We chose a Python project, since that is the only language we know (we are
first years). We looked at a few issues in SymPy and PyMC. They were a bit too
complex for us and a lot of them already had pull requests open. We chose
SymPy #30902, which lists 35 defects in the code that finds derivatives of
matrix expressions. Each defect has a short example that reproduces it. We
wanted to finish at least 10 of them. The table in section 4 shows where we
actually are.

## 2. Setup

We forked the original SymPy repository, cloned our fork, and added the team as
collaborators so everyone can upload their work to the same fork. We used
VS Code to run and test the code, with Python 3.14.8 on a Mac. Every branch
started from the same commit, c508f90.

## 3. How we handle each defect

1. Run the example from the issue and watch it fail.
2. Find out why it fails.
3. Make the smallest fix.
4. Add a test, then run it with SymPy's quality checks
   (`ruff check sympy` and `python bin/test quality`).
5. Commit and push to our fork, on our own branch.

Nobody commits to master and we never open a pull request. Each person owns
their own files so our changes don't collide.

## 4. Where each defect stands

| Item | Problem | Status |
|---|---|---|
| 4 | Matrix to a power like 1/2 gives a nonsense sum | Done in our fork |
| 2 | Derivative of exp(z + 1) loses the "+ 1" | Fix proposed, tried in a separate copy, not yet in our fork |
| 15 | Derivative of a Hadamard product crashes | Fix proposed, tried in a separate copy, not yet in our fork |
| 13 | Bad axes are accepted | [FILL IN] |
| 16 | NotImplementedError leaks out of .diff() | Plan only |

### Item 4 (branch item-4-Laksh)

The derivative of a matrix power assumed a whole-number power. For 1/2 it
printed a nonsense sum from 0 to -1/2. In arrayexpr_derivatives.py we now raise
NotImplementedError when the power is known not to be a whole number. Powers
like 3 and k + 1 print the same as before. The test
test_array_derive_matpow_non_integer_exponent passes, and ruff and the quality
check passed.

We never watched the new test fail without the fix. The old code returned a sum
and never raised an error, so the test could not have passed without it. We
want to try more cases later, for example negative powers.

### Round 2

**Item 2: elementwise functions.** SymPy sometimes loses part of a function's
argument while taking a derivative. For exp(z + 1) it can return exp(z), with
no error message, so the answer is silently wrong. This happens because the code
keeps only the function type and drops the argument. Our idea is to keep the
whole expression whenever the argument is more than just the variable itself,
in both places where this is done. Status: we reproduced it on the original
code and tried the fix and a regression test in a separate copy of SymPy (the
ZIP file we started from had no Git version information). The test passes
there, and small checks with 2x2 matrices gave the expected results. Still to
do: redo it in our fork, run the full test suite and run the quality checks.

**Item 15: Hadamard product.** A Hadamard product multiplies two matrices
entry by entry. Differentiating one with array_derive raises
NotImplementedError instead of giving the derivative. The cause looks like an
unfinished special handler that is picked before the general matrix-expression
handler, which can already deal with this kind of expression. Our idea is to
remove the unfinished handler so the existing one is used. Status: the same as
item 2. We reproduced it on the original code, and the fix and its regression
test pass in a separate copy, with small 2x2 checks matching. Still to do:
redo it in our fork, then the full tests and quality checks.

**Item 13: bad axes.** Every axis you name should exist and belong to only one
group. These calls are wrongly accepted or crash with an unhelpful message:

| Call | What happens now | Why it is wrong |
|---|---|---|
| ArrayContraction(M, (-1, 0)) | accepted, shape (2,) | negative axis reinterpreted silently |
| ArrayContraction(M, (0, 0)) | accepted, shape (2,) | an axis tied to itself |
| ArrayContraction(A3, (0, 1), (1, 2)) | accepted, shape () | axis 1 is in two groups |
| ArrayContraction(M, (0, 5)) | IndexError: tuple index out of range | axis 5 does not exist |
| ArrayDiagonal(M, (-1, 0)) | accepted | only repeats inside one group are rejected |

The validation only checks that tied axes have the same length. It does not
check that they exist or are unique. Our idea is to check the axes first and
reject negative or repeated ones. Status: [FILL IN: code and test status].

**Item 16: NotImplementedError leaking from .diff().** For unsupported inputs,
.diff() currently stops with an error, where the issue expects an unevaluated
Derivative. Our plan is to let the low-level routines signal "not supported"
instead of raising, and have the higher level build the unevaluated derivative.
Status: plan only. Open question: this touches the same MatPow rule as item 4
and would change what item 4's test expects, so we need to settle the order
and the behaviour before we write any code.

## 5. AI use

We used Claude (Anthropic) to explain the issue and the code and to suggest the
item 4 fix and test. We typed and ran them ourselves. The issue itself was
written with an AI agent. [FILL IN: any AI used for the round 2 write-ups and
fixes, with the tool name.]

## 6. Team

Our team uses one shared fork and we are all collaborators. Nobody commits to
master and we never open a pull request.

## 7. Limits

- Only items marked "Done in our fork" are finished. The rest are ideas or
  tests in a separate copy.
- We have not run the whole SymPy test suite.
- Tested on macOS with Python 3.14.8 only.
- SymPy's maintainers have not reviewed any of this.
