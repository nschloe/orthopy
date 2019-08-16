import numpy
import sympy

from ..tools import line_tree


def recurrence_coefficients(n, standardization, symbolic=False):
    S = numpy.vectorize(sympy.S) if symbolic else lambda x: x
    sqrt = numpy.vectorize(sympy.sqrt) if symbolic else numpy.sqrt
    # TODO replace by sqrt once <https://github.com/numpy/numpy/issues/10363> is fixed
    sS = sympy.S if symbolic else lambda x: x
    ssqrt = sympy.sqrt if symbolic else numpy.sqrt
    pi = sympy.pi if symbolic else numpy.pi

    # Check <https://en.wikipedia.org/wiki/Hermite_polynomials> for the different
    # standardizations.
    N = numpy.array([sS(k) for k in range(n)])
    if standardization in ["probabilist", "monic"]:
        p0 = 1
        a = numpy.ones(n, dtype=int)
        b = numpy.zeros(n, dtype=int)
        c = N
        c[0] = ssqrt(pi)  # only used for custom scheme
    elif standardization == "physicist":
        p0 = 1
        a = numpy.full(n, 2, dtype=int)
        b = numpy.zeros(n, dtype=int)
        c = 2 * N
        c[0] = ssqrt(pi)  # only used for custom scheme
    else:
        assert (
            standardization == "normal"
        ), "Unknown standardization '{}'.".format(standardization)
        p0 = 1 / sqrt(sqrt(pi))
        a = sqrt(S(2) / (N + 1))
        b = numpy.zeros(n, dtype=int)
        c = sqrt(S(N) / (N + 1))
        c[0] = numpy.nan

    return p0, a, b, c


def tree(X, n, standardization, symbolic=False):
    return line_tree(
        X,
        *recurrence_coefficients(n, standardization=standardization, symbolic=symbolic),
    )
