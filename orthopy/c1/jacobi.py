import itertools
import math

import numpy
import sympy

from ..helpers import Eval1D


def tree(n, *args, **kwargs):
    return list(itertools.islice(Eval(*args, **kwargs), n + 1))


def plot(n, *args, **kwargs):
    import dufte
    import matplotlib.pyplot as plt

    plt.style.use(dufte.style)

    x = numpy.linspace(-1.0, 1.0, 100)
    for k, level in enumerate(itertools.islice(Eval(x, *args, **kwargs), n + 1)):
        plt.plot(x, level, label=f"n={k}")

    plt.grid(axis="x")
    dufte.legend()
    ax = plt.gca()

    alpha, beta, scaling = args
    if alpha == beta:
        if alpha == 0:
            plt.title(f"Legendre polynomials (scaling={scaling})")
        elif alpha == -0.5:
            plt.title(f"Chebyshev 1 polynomials (scaling={scaling})")
        elif alpha == +0.5:
            plt.title(f"Chebyshev 2 polynomials (scaling={scaling})")
        else:
            plt.title(f"Gegenbauer polynomials (λ={alpha}, scaling={scaling})")
    else:
        plt.title(f"Jacobi polynomials (α={alpha}, β={beta}, scaling={scaling})")
    ax.spines["right"].set_visible(True)
    ax.spines["left"].set_visible(True)


def show(*args, **kwargs):
    import matplotlib.pyplot as plt

    plot(*args, **kwargs)
    plt.show()


def savefig(filename, *args, **kwargs):
    import matplotlib.pyplot as plt

    plot(*args, **kwargs)
    plt.savefig(filename, transparent=True, bbox_inches="tight")


class Eval(Eval1D):
    def __init__(self, X, *args, **kwargs):
        super().__init__(X, RecurrenceCoefficients(*args, **kwargs))


class RecurrenceCoefficients:
    def __init__(self, alpha, beta, scaling, symbolic=False):
        cls = {"monic": RCMonic, "classical": RCClassical, "normal": RCNormal}[scaling]
        self.rc = cls(alpha, beta, symbolic)
        self.p0 = self.rc.p0

    def __getitem__(self, N):
        return self.rc[N]


class RCMonic:
    """Generate the recurrence coefficients a_k, b_k, c_k in

    P_{k+1}(x) = (a_k x - b_k) * P_{k}(x) - c_k * P_{k-1}(x)

    for the Jacobi polynomials which are orthogonal on [-1, 1] with respect to the
    weight w(x)=[(1-x)^alpha]*[(1+x)^beta]; see
    <https://en.wikipedia.org/wiki/Jacobi_polynomials#Recurrence_relations>.
    """

    def __init__(self, alpha, beta, symbolic):
        self.alpha = alpha
        self.beta = beta
        self.gamma = sympy.gamma if symbolic else lambda x: math.gamma(float(x))

        self.frac = sympy.Rational if symbolic else lambda x, y: x / y
        self.nan = None if symbolic else math.nan
        self.one = 1 if symbolic else 1.0

        self.p0 = self.one

    def __getitem__(self, N):
        frac = self.frac
        alpha = self.alpha
        beta = self.beta

        a = self.one

        if N == 0:
            b = frac(beta - alpha, alpha + beta + 2)
        else:
            b = frac(
                beta ** 2 - alpha ** 2,
                (2 * N + alpha + beta) * (2 * N + alpha + beta + 2),
            )

        # Note that we have the treat the case N==1 separately to avoid division by 0
        # for alpha=beta=-1/2.
        if N == 0:
            # c[0] is not used in the actual recurrence, but is traditionally defined as
            # the integral of the weight function of the domain, i.e.,
            # ```
            # int_{-1}^{+1} (1-x)^a * (1+x)^b dx =
            #     2^(a+b+1) * Gamma(a+1) * Gamma(b+1) / Gamma(a+b+2).
            # ```
            # This is bad practice; the value could accidentally be used.
            c = self.nan
        elif N == 1:
            c = frac(
                4 * (1 + alpha) * (1 + beta),
                (2 + alpha + beta) ** 2 * (3 + alpha + beta),
            )
        else:
            c = frac(
                4 * (N + alpha) * (N + beta) * N * (N + alpha + beta),
                (2 * N + alpha + beta) ** 2
                * (2 * N + alpha + beta + 1)
                * (2 * N + alpha + beta - 1),
            )
        return a, b, c


class RCClassical:
    def __init__(self, alpha, beta, symbolic):
        self.frac = sympy.Rational if symbolic else lambda x, y: x / y
        self.nan = None if symbolic else math.nan
        self.alpha = alpha
        self.beta = beta

        self.p0 = 1 if symbolic else 1.0

        # gamma = sympy.gamma if symbolic else lambda x: math.gamma(float(x))
        # self.int_1 = (
        #     2 ** (alpha + beta + 1)
        #     * gamma(alpha + 1)
        #     * gamma(beta + 1)
        #     / gamma(alpha + beta + 2)
        # )

    def __getitem__(self, N):
        frac = self.frac
        alpha = self.alpha
        beta = self.beta

        # Treat N = 0 separately to avoid division by 0 for alpha = beta = -1/2.
        if N == 0:
            a = frac(alpha + beta + 2, 2)
            b = frac(beta - alpha, 2)
            c = self.nan
        else:
            a = frac(
                (2 * N + alpha + beta + 1) * (2 * N + alpha + beta + 2),
                2 * (N + 1) * (N + alpha + beta + 1),
            )
            b = frac(
                (beta ** 2 - alpha ** 2) * (2 * N + alpha + beta + 1),
                2 * (N + 1) * (N + alpha + beta + 1) * (2 * N + alpha + beta),
            )
            c = frac(
                (N + alpha) * (N + beta) * (2 * N + alpha + beta + 2),
                (N + 1) * (N + alpha + beta + 1) * (2 * N + alpha + beta),
            )

        return a, b, c


class RCNormal:
    def __init__(self, alpha, beta, symbolic):
        self.frac = sympy.Rational if symbolic else lambda x, y: x / y
        self.sqrt = sympy.sqrt if symbolic else math.sqrt
        self.nan = None if symbolic else math.nan
        self.alpha = alpha
        self.beta = beta

        gamma = sympy.gamma if symbolic else lambda x: math.gamma(float(x))
        self.int_1 = (
            2 ** (alpha + beta + 1)
            * gamma(alpha + 1)
            * gamma(beta + 1)
            / gamma(alpha + beta + 2)
        )
        self.p0 = self.sqrt(1 / self.int_1)

    def __getitem__(self, N):
        frac = self.frac
        sqrt = self.sqrt
        alpha = self.alpha
        beta = self.beta

        # Treat N==0 separately to avoid division by 0 for alpha=beta=-1/2 (Chebyshev 1)
        # and alpha=beta=0 (Legendre).
        if N == 0:
            t = sqrt(frac(alpha + beta + 3, (alpha + 1) * (beta + 1)))
            a = frac(alpha + beta + 2, 2) * t
            b = frac(beta - alpha, 2) * t
        else:
            t = sqrt(
                frac(
                    (2 * N + alpha + beta + 1) * (2 * N + alpha + beta + 3),
                    (N + 1) * (N + alpha + 1) * (N + beta + 1) * (N + alpha + beta + 1),
                )
            )
            a = frac(2 * N + alpha + beta + 2, 2) * t
            b = frac(beta ** 2 - alpha ** 2, 2 * (2 * N + alpha + beta)) * t

        if N == 0:
            c = self.nan
        elif N == 1:
            c = frac(4 + alpha + beta, 2 + alpha + beta) * sqrt(
                frac(
                    (1 + alpha) * (1 + beta) * (5 + alpha + beta),
                    2 * (2 + alpha) * (2 + beta) * (2 + alpha + beta),
                )
            )
        else:
            c = frac(2 * N + alpha + beta + 2, 2 * N + alpha + beta) * sqrt(
                frac(
                    N
                    * (N + alpha)
                    * (N + beta)
                    * (N + alpha + beta)
                    * (2 * N + alpha + beta + 3),
                    (N + 1)
                    * (N + alpha + 1)
                    * (N + beta + 1)
                    * (N + alpha + beta + 1)
                    * (2 * N + alpha + beta - 1),
                )
            )

        return a, b, c
