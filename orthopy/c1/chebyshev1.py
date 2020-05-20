import itertools

import sympy

from ..tools import Iterator1D
from . import gegenbauer


def tree(n, *args, **kwargs):
    return list(itertools.islice(Iterator(*args, **kwargs), n + 1))


class Iterator(Iterator1D):
    """Chebyshev polynomials of the first kind. The first few are:

    standardization == "monic":
        1
        x
        x**2 - 1/2
        x**3 - 3*x/4
        x**4 - x**2 + 1/8
        x**5 - 5*x**3/4 + 5*x/16

    standardization == "classical":
        1
        x/2
        3*x**2/4 - 3/8
        5*x**3/4 - 15*x/16
        35*x**4/16 - 35*x**2/16 + 35/128
        63*x**5/16 - 315*x**3/64 + 315*x/256

    standardization == "normal":
        1/sqrt(pi)
        sqrt(2)*x/sqrt(pi)
        2*sqrt(2)*x**2/sqrt(pi) - sqrt(2)/sqrt(pi)
        4*sqrt(2)*x**3/sqrt(pi) - 3*sqrt(2)*x/sqrt(pi)
        8*sqrt(2)*x**4/sqrt(pi) - 8*sqrt(2)*x**2/sqrt(pi) + sqrt(2)/sqrt(pi)
        16*sqrt(2)*x**5/sqrt(pi) - 20*sqrt(2)*x**3/sqrt(pi) + 5*sqrt(2)*x/sqrt(pi)
    """

    def __init__(self, X, standardization, *args, **kwargs):
        if standardization == "monic":
            iterator = IteratorRCMonic(*args, **kwargs)
        elif standardization == "classical":
            # p(1) = (n+alpha over n)   (=1 if alpha=0)
            iterator = IteratorRCClassical(*args, **kwargs)
        else:
            valid = ", ".join(["monic", "classical", "normal"])
            assert (
                standardization == "normal"
            ), f"Unknown standardization '{standardization}'. (valid: {valid})"
            iterator = IteratorRCNormal(*args, **kwargs)

        super().__init__(X, iterator)


class IteratorRCMonic(gegenbauer.IteratorRCMonic):
    def __init__(self, symbolic=False):
        one_half = sympy.S(1) / 2 if symbolic else 0.5
        super().__init__(-one_half, symbolic)


class IteratorRCClassical(gegenbauer.IteratorRCClassical):
    def __init__(self, symbolic=False):
        one_half = sympy.S(1) / 2 if symbolic else 0.5
        super().__init__(-one_half, symbolic)


class IteratorRCNormal(gegenbauer.IteratorRCNormal):
    def __init__(self, symbolic=False):
        one_half = sympy.S(1) / 2 if symbolic else 0.5
        super().__init__(-one_half, symbolic)
