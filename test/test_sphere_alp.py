# -*- coding: utf-8 -*-
#
from __future__ import division

import matplotlib.pyplot as plt
import numpy
from numpy import sqrt
import orthopy
import pytest
from scipy.special import gammaln


def P4_exact(x):
    # pylint: disable=too-many-locals
    sqrt1mx2 = numpy.sqrt(1 - x**2)

    try:
        p0_0 = numpy.ones(x.shape)
    except AttributeError:
        p0_0 = 1.0
    #
    p1p1 = -sqrt(1 - x**2)
    p1_0 = x
    p1m1 = -0.5 * p1p1
    #
    p2p2 = 3*(1 - x**2)
    p2p1 = -3*x*sqrt1mx2
    p2_0 = 0.5 * (3*x**2 - 1)
    p2m1 = -p2p1 / 6
    p2m2 = p2p2 / 24
    #
    p3p3 = -15 * sqrt1mx2**3
    p3p2 = 15 * x * (1 - x**2)
    p3p1 = -1.5 * (5*x**2 - 1) * sqrt1mx2
    p3_0 = 0.5 * (5*x**3 - 3*x)
    p3m1 = -p3p1 / 12
    p3m2 = +p3p2 / 120
    p3m3 = -p3p3 / 720
    #
    p4p4 = 105 * (1 - x**2)**2
    p4p3 = -105 * x * sqrt1mx2**3
    p4p2 = 7.5 * (7*x**2 - 1) * (1 - x**2)
    p4p1 = -2.5 * (7*x**3 - 3*x) * sqrt1mx2
    p4_0 = (35*x**4 - 30*x**2 + 3) / 8
    p4m1 = -p4p1 / 20
    p4m2 = +p4p2 / 360
    p4m3 = -p4p3 / 5040
    p4m4 = +p4p4 / 40320

    return [
        [p0_0],
        [p1m1, p1_0, p1p1],
        [p2m2, p2m1, p2_0, p2p1, p2p2],
        [p3m3, p3m2, p3m1, p3_0, p3p1, p3p2, p3p3],
        [p4m4, p4m3, p4m2, p4m1, p4_0, p4p1, p4p2, p4p3, p4p4],
        ]


numpy.random.seed(10)


@pytest.mark.parametrize(
    'x', [1.0e-1, 1.0e-4, numpy.random.rand(3, 2)]
    )
def test_unnormalized(x, tol=1.0e-12):
    L = 4
    vals = orthopy.sphere.alp_tree(L, x)
    exacts = P4_exact(x)
    for val, ex in zip(vals, exacts):
        for v, e in zip(val, ex):
            assert numpy.all(numpy.abs(v - e) < tol * numpy.abs(e))
    return


@pytest.mark.parametrize(
    'x', [1.0e-1, 1.0e-4, numpy.random.rand(3, 2)]
    )
def test_spherical(x, tol=1.0e-12):
    '''Test spherical harmonic normalization.
    '''
    L = 4
    vals = orthopy.sphere.alp_tree(L, x, normalization='spherical')
    exacts = P4_exact(x)

    # pylint: disable=consider-using-enumerate
    for L in range(len(exacts)):
        for k, m in enumerate(range(-L, L+1)):
            exacts[L][k] *= \
                numpy.sqrt((2*L+1) / 4 / numpy.pi) \
                * numpy.exp(0.5 * (gammaln(L-m+1) - gammaln(L+m+1)))

    for val, ex in zip(vals, exacts):
        for v, e in zip(val, ex):
            assert numpy.all(numpy.abs(v - e) < tol * numpy.abs(e))
    return


@pytest.mark.parametrize(
    'x', [1.0e-1, 1.0e-4, numpy.random.rand(3, 2)]
    )
def test_full(x, tol=1.0e-12):
    L = 4
    vals = orthopy.sphere.alp_tree(L, x, normalization='full')
    exacts = P4_exact(x)

    # pylint: disable=consider-using-enumerate
    for L in range(len(exacts)):
        for k, m in enumerate(range(-L, L+1)):
            # sqrt((2*L+1) / 4 / pi * factorial(l-m) / factorial(l+m))
            exacts[L][k] *= \
                numpy.sqrt((2*L+1) / 2) \
                * numpy.exp(0.5 * (gammaln(L-m+1) - gammaln(L+m+1)))

    for val, ex in zip(vals, exacts):
        for v, e in zip(val, ex):
            assert numpy.all(numpy.abs(v - e) < tol * numpy.abs(e))
    return


@pytest.mark.parametrize(
    'x', [1.0e-1, 1.0e-4, numpy.random.rand(3, 2)]
    )
def test_schmidt(x, tol=1.0e-12):
    L = 4
    vals = orthopy.sphere.alp_tree(L, x, normalization='schmidt')
    exacts = P4_exact(x)

    # pylint: disable=consider-using-enumerate
    for L in range(len(exacts)):
        for k, m in enumerate(range(-L, L+1)):
            # sqrt((2*L+1) / 4 / pi * factorial(l-m) / factorial(l+m))
            exacts[L][k] *= \
                2 * numpy.exp(0.5 * (gammaln(L-m+1) - gammaln(L+m+1)))

    for val, ex in zip(vals, exacts):
        for v, e in zip(val, ex):
            assert numpy.all(numpy.abs(v - e) < tol * numpy.abs(e))
    return


def test_show():
    L = 4
    x = numpy.linspace(-1.0, +1.0, 500)
    vals = orthopy.sphere.alp_tree(
            L, x, normalization='full',
            with_condon_shortley_phase=False
            )

    for val in vals[L]:
        plt.plot(x, val)

    plt.xlim(-1, +1)
    # plt.ylim(-2, +2)
    plt.tick_params(
        axis='both',
        which='both',
        bottom='off',
        top='off',
        left='off',
        right='off',
        labelbottom='off',
        labelleft='off'
        )
    plt.grid()
    return


if __name__ == '__main__':
    x_ = 0.43
    # x_ = numpy.random.rand(3, 2)
    # test_unnormalized(x=x_)
    # test_full(x=x_)
    test_show()
    plt.show()