sympy hadamard product fixes

============================

hey, so this is my writeup for two bug fixes i made in sympy, both
around

hadamard products (multiplying two matrices entry by entry, NOT normal
matrix

multiplication).

fix 1: wrong orientation check when converting array -\> matrix
expressions

fix 2: derivatives of hadamard products crashing (issue #30902, item 15)

they're separate changes in separate files, so i wrote them up
separately

below. quick glossary first so nothing sounds like gibberish.

quick glossary

------------------------------------------------------------------------

derivative how much the answer changes if you nudge the input

matrix a grid of numbers

hadamard product multiply two grids entry by entry (top-left with
top-left etc)

dispatch sympy's "which function handles this type of object?" lookup.

                 it always picks the MOST SPECIFIC handler

fallback the general handler used when there's no special one

stub a placeholder function that only raises an error

=====================================================================

FIX 1: orientation check in identify_hadamard_products

=====================================================================

file:

sympy/tensor/array/expressions/from_array_to_matrix.py

(inside identify_hadamard_products -\> check_transpose)

what was wrong

------------------------------------------------------------------------

indices come in 2 types:

-   contraction indices are \>= 0

-   diagonal indices are stored as -1-i

the old code turned the diagonal ones back into i before comparing. so
when a

group had BOTH kinds, stuff collided (0 and -1 both became 0),
everything

looked "already sorted", and the transpose never got flipped when it
needed

to. result = wrong matrix expression after converting back.

what i did

------------------------------------------------------------------------

if a group mixes both kinds, each index now gets mapped to (i \< 0, i)
before

sorting. that puts contraction indices first and diagonal ones after, so

nothing collides anymore. groups with only one kind of index work
exactly

like before, so nothing else should change.

the new code:

    def check_transpose(x):

        # Contraction indices are >= 0, diagonal indices are -1-i.

        # In a group that mixes both kinds, mapping -1-i onto i makes

        # distinct indices collide (0 and -1 both become 0), so every

        # orientation looks "sorted". Order contraction indices before

        # diagonal indices in that case.

        x = list(x)

        if any(i < 0 for i in x) and any(i >= 0 for i in x):

            x = [(i < 0, i) for i in x]

        else:

            x = [i if i >= 0 else -1-i for i in x]

        return x == sorted(x)

tests for fix 1

------------------------------------------------------------------------

(a) sympy/tensor/array/expressions/tests/test_convert_array_to_matrix.py

    test_hadamard_product_orientation_roundtrip (added at the end of the
    file)

    takes a bunch of expressions (transposed factors, longer chains,

    non-square matrices, vectors, traces), does matrix -\> array -\>
    matrix and

    checks:

    -   the actual values are still the same after the round trip

    -   doing the conversion twice gives the same thing (idempotent)

    -   the symbolic k x k cases come back exactly equal

    it also uses a little helper \_value(e) that takes the explicit
    value of an

    expression (the trace of the explicit matrix if it's a Trace).

(b) sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py

    test_array_derive_trace_hadamard_product_matmul (added at the end)

    checks that d/dX of Trace(H(A*X, B*X)\*C) equals

    A.T*H(B*X, C.T) + B.T*H(A*X, C.T)

    and double checks it against derive_by_array on the fully explicit
    version.

=====================================================================

FIX 2: derivative of a hadamard product crashed (issue #30902, item 15)

=====================================================================

files changed (all in the patch item15_hadamard_fallback.patch):

sympy/tensor/array/expressions/arrayexpr_derivatives.py (the fix)

sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py (4
tests)

sympy/matrices/expressions/tests/test_derivatives.py (1 test)

the story in 4 sentences

------------------------------------------------------------------------

1.  sympy had a SPECIAL handler for HadamardProduct inside array_derive,
    and

    all it did was raise NotImplementedError (a stub).

2.  sympy ALSO has a GENERAL handler (for MatrixExpr) that can actually
    do the job.

3.  since the special one is more specific, sympy always picked it and
    never

    reached the general one that works.

4.  fix = delete the stub. sympy now uses the general handler, which
    already

    works and was already tested.

analogy: a shop has a "Specialist" counter with a "Closed" sign and a

"General" counter that can serve you. the system always sent you to the

Specialist one first. i removed the Specialist counter so you go to
General.

what i changed in the code

------------------------------------------------------------------------

removed this:

    @array_derive.register(HadamardProduct)

    def _(expr: HadamardProduct, x: Expr):

        raise NotImplementedError()

and removed the HadamardProduct import from arrayexpr_derivatives.py
since

nothing uses it there anymore. that's it, only deletions in the real
code.

note: a plain H.diff(M) actually worked even before. the bug showed up
when

the hadamard product was INSIDE Determinant, Inverse or MatPow, or when

array_derive was called on it directly. that's why nobody caught it.

tests for fix 2

------------------------------------------------------------------------

all in test_arrayexpr_derivatives.py:

1)  test_array_derive_hadamard_product_uses_matrixexpr_fallback

    structural check that array_derive.dispatch(HadamardProduct) is the
    same

    as array_derive.dispatch(MatrixExpr), so the stub can't sneak back
    in.

    also checks the result equals differentiating the converted array

    expression, and the shape is (3, 3, 3, 3).

2)  test_array_derive_hadamard_product_numeric

    compares sympy's answer with a slow trusted method (differentiate
    every

    entry one by one using derive_by_array) for: derivative wrt either
    factor,

    the same matrix twice (M o M, M o N o M), nested hadamard products,

    H*M, M*H, H*H, H+M, Transpose(H), Trace(H), Trace(H*H.T).

3)  test_array_derive_hadamard_product_nested_in_rules

    hadamard product inside other operations: Determinant, Inverse,
    MatPow

    (powers 2 and -2). numbers chosen so M o N is invertible.

4)  test_array_derive_hadamard_product_edge_cases

    -   variable not in the expression -\> ZeroArray(3, 3, 3, 3)

    -   non-square matrices (2x3)

    -   column vectors (3x1), row vectors (1x3), 1x1 matrices

    -   symbolic dimensions keep shape (k, k, k, k)

    -   an expression the fallback can't convert (a fake Opaque
        MatrixExpr)

        still raises NotImplementedError instead of looping forever

and in sympy/matrices/expressions/tests/test_derivatives.py:

5)  test_derivative_of_hadamard_product_in_matrix_functions

    checks .diff(M) on Determinant(H), Inverse(H), MatPow(H, 2),
    Trace(H\*H)

    against the entry-by-entry method.

before vs after

------------------------------------------------------------------------

before the fix:

-   array_derive(H, M), Determinant(H), Inverse(H) all crash with

    NotImplementedError

-   the new tests: 4 failed (so the tests really do catch the bug)

after the fix:

-   all of those work, and match the trusted answer (True)

-   edge cases all correct

-   the new tests: 4 passed

-   i also ran 1092 existing tests across the tensor and matrix code,
    all

    pass, and the style/documentation checks pass too

the saved outputs are in demo_BEFORE_fix.txt and demo_AFTER_fix.txt.

=====================================================================

how to run everything

=====================================================================

run from the sympy repo folder.

fix 1 tests:

pytest
sympy/tensor/array/expressions/tests/test_convert_array_to_matrix.py -k
orientation_roundtrip

pytest
sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py -k
trace_hadamard

fix 2 tests:

pytest -q
sympy/tensor/array/expressions/tests/test_arrayexpr_derivatives.py -k
hadamard

pytest -q sympy/matrices/expressions/tests/test_derivatives.py -k
hadamard

fix 2 demo script (prints WORKS/CRASH and True/False for each case):

cd /home/claude/sympy/sympy

PYTHONPATH=. python3 /home/claude/demo_item15.py

to show the "before" state live: git stash, run the commands, then git
stash pop

to apply the patch on a fresh checkout:

git apply item15_hadamard_fallback.patch

=====================================================================

demo order (if i have to present it)

=====================================================================

1.  initial error (before): show demo_BEFORE_fix.txt part 1

    "i ask sympy how a hadamard product changes when one matrix changes
    and it

    crashes with NotImplementedError, also inside Determinant and
    Inverse."

2.  failing tests (before): end of demo_BEFORE_fix.txt, "4 failed"

    "on the original code all 4 fail, so the tests actually detect the
    bug."

3.  working case (after): demo_AFTER_fix.txt parts 1 and 2

    "after deleting the stub all three work, and to be sure they're
    CORRECT

    (not just 'no crash') i compare with differentiating every entry one
    by

    one. they match: True."

4.  edge cases (after): demo_AFTER_fix.txt part 3

    "non-square, same matrix twice, and a variable not in the expression

    (correctly gives zero)."

5.  nothing else broke: 1092 existing tests pass.

=====================================================================

questions people might ask

=====================================================================

why just delete code?

the correct logic already exists in the general handler. writing a new
one

would duplicate it and could drift out of sync.

how do you know the answers are right?

i compared with entry-by-entry differentiation, which is independent of
the

fast method. exact numbers, no rounding.

could this cause an endless loop?

no. the general handler has a guard (cg == expr) that raises an error if
the

conversion changes nothing, and there's a test for it (the Opaque one).

does it fix everything in issue #30902?

no, only item 15. the other items are separate and untouched.

is fix 1 related to fix 2?

both are about hadamard products in the array expression code, but
they're

different bugs in different files and fixed separately.
