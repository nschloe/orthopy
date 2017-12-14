# -*- coding: utf-8 -*-
#
from __future__ import division

import numpy
import orthopy
import pytest
import quadpy
import sympy
from sympy import sqrt, pi


def test_orthonormality(tol=1.0e-13):
    '''Make sure that the polynomials are orthonormal.
    '''
    n = 4
    # Choose a scheme of order at least 2*n.
    scheme = quadpy.sphere.Lebedev(9)

    # normality
    def ff(azimuthal, polar):
        tree = numpy.concatenate(
                orthopy.sphere.sph_tree(
                    n, polar, azimuthal, normalization='quantum mechanic'
                    ))
        return tree * numpy.conjugate(tree)

    val = quadpy.sphere.integrate_spherical(ff, rule=scheme)
    assert numpy.all(abs(val - 1) < tol)

    # orthogonality
    def f_shift(azimuthal, polar):
        tree = numpy.concatenate(
                orthopy.sphere.sph_tree(
                    n, polar, azimuthal, normalization='quantum mechanic'
                    ))
        return tree * numpy.roll(tree, 1, axis=0)

    val = quadpy.sphere.integrate_spherical(f_shift, rule=scheme)
    assert numpy.all(abs(val) < tol)
    return


def test_schmidt_orthonormality(tol=1.0e-12):
    '''Make sure that the polynomials are orthonormal.
    '''
    n = 4
    # Choose a scheme of order at least 2*n.
    scheme = quadpy.sphere.Lebedev(9)

    # normality
    def ff(azimuthal, polar):
        tree = numpy.concatenate(
                orthopy.sphere.sph_tree(
                    n, polar, azimuthal, normalization='schmidt'
                    ))
        return tree * numpy.conjugate(tree)

    vals = quadpy.sphere.integrate_spherical(ff, rule=scheme)
    # split into levels
    levels = [
            vals[0:1], vals[1:4], vals[4:9], vals[9:16], vals[16:25]
            ]
    for k, level in enumerate(levels):
        assert numpy.all(abs(level - 4*numpy.pi/(2*k+1)) < tol)

    # orthogonality
    def f_shift(azimuthal, polar):
        tree = numpy.concatenate(
                orthopy.sphere.sph_tree(
                    n, polar, azimuthal, normalization='schmidt'
                    ))
        return tree * numpy.roll(tree, 1, axis=0)

    val = quadpy.sphere.integrate_spherical(f_shift, rule=scheme)
    assert numpy.all(abs(val) < tol)
    return


# pylint: disable=too-many-locals
def sph_exact2(theta, phi):
    # Exact values from
    # <https://en.wikipedia.org/wiki/Table_of_spherical_harmonics>.
    try:
        assert numpy.all(theta.shape == phi.shape)
        y0_0 = numpy.full(theta.shape, sqrt(1 / pi) / 2)
    except AttributeError:
        y0_0 = sqrt(1 / pi) / 2

    sin = numpy.vectorize(sympy.sin)
    cos = numpy.vectorize(sympy.cos)
    exp = numpy.vectorize(sympy.exp)

    sin_theta = sin(theta)
    cos_theta = cos(theta)

    # pylint: disable=invalid-unary-operand-type
    y1m1 = +sin_theta * exp(-1j*phi) * sqrt(3 / pi / 2) / 2
    y1_0 = +cos_theta * sqrt(3 / pi) / 2
    y1p1 = -sin_theta * exp(+1j*phi) * sqrt(3 / pi / 2) / 2
    #
    y2m2 = +sin_theta**2 * exp(-1j*2*phi) * sqrt(15 / pi / 2) / 4
    y2m1 = +(sin_theta * cos_theta * exp(-1j*phi)) * (sqrt(15 / pi / 2) / 2)
    y2_0 = +(3*cos_theta**2 - 1) * sqrt(5 / pi) / 4
    y2p1 = -(sin_theta * cos_theta * exp(+1j*phi)) * (sqrt(15 / pi / 2) / 2)
    y2p2 = +sin_theta**2 * exp(+1j*2*phi) * sqrt(15 / pi / 2) / 4
    return [
        [y0_0],
        [y1m1, y1_0, y1p1],
        [y2m2, y2m1, y2_0, y2p1, y2p2],
        ]


@pytest.mark.parametrize(
    'theta,phi', [
        (sympy.Rational(1, 10), sympy.Rational(16, 5)),
        (sympy.Rational(1, 10000), sympy.Rational(7, 100000)),
        # (
        #   numpy.array([sympy.Rational(3, 7), sympy.Rational(1, 13)]),
        #   numpy.array([sympy.Rational(2, 5), sympy.Rational(2, 3)]),
        # )
        ]
    )
def test_spherical_harmonics(theta, phi):
    L = 2
    exacts = sph_exact2(theta, phi)
    vals = orthopy.sphere.sph_tree(
            L, theta, phi, normalization='quantum mechanic', symbolic=True
            )

    for val, ex in zip(vals, exacts):
        for v, e in zip(val, ex):
            assert numpy.all(numpy.array(sympy.simplify(v - e)) == 0)
    return


@pytest.mark.parametrize(
    'theta,phi', [
        (1.0e-1, 16.0/5.0),
        (1.0e-4, 7.0e-5),
        ]
    )
def test_spherical_harmonics_numpy(theta, phi):
    L = 2
    exacts = sph_exact2(theta, phi)
    vals = orthopy.sphere.sph_tree(
            L, theta, phi, normalization='quantum mechanic'
            )

    cmplx = numpy.vectorize(complex)
    for val, ex in zip(vals, exacts):
        assert numpy.all(abs(val - cmplx(ex)) < 1.0e-12)
    return


def test_write():
    def sph22(polar, azimuthal):
        out = orthopy.sphere.sph_tree(
            5, polar, azimuthal, normalization='quantum mechanic'
            )[5][3]
        # out = numpy.arctan2(numpy.imag(out), numpy.real(out))
        out = abs(out)
        return out

    orthopy.sphere.write('sph.vtu', sph22)
    return


if __name__ == '__main__':
    test_write()
