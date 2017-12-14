# -*- coding: utf-8 -*-
#
from __future__ import division

import numpy
import orthopy
import quadpy


def test_orthonormal(tol=1.0e-14):
    '''Make sure that the polynomials are orthonormal
    '''
    n = 4
    # Choose a scheme of order at least 2*n.
    scheme = quadpy.quadrilateral.Dunavant(4)

    quad = [[[-1.0, -1.0], [+1.0, -1.0]], [[-1.0, +1.0], [+1.0, +1.0]]]

    # normality
    def ff(x):
        tree = numpy.concatenate(
                orthopy.quadrilateral.orth_tree(n, x)
                )
        return tree * tree

    val = quadpy.quadrilateral.integrate(ff, quad, scheme)
    print(val)
    assert numpy.all(abs(val - 1) < tol)

    # # orthogonality
    # def f_shift(x):
    #     tree = numpy.concatenate(
    #             orthopy.quadrilateral.orth_tree(n, x)
    #             )
    #     return tree * numpy.roll(tree, 1, axis=0)

    # val = quadpy.quadrilateral.integrate(f_shift, quad, scheme)
    # assert numpy.all(abs(val) < tol)
    return


def test_show(n=2, r=1):
    def f(X):
        return orthopy.quadrilateral.orth_tree(n, X)[n][r]

    orthopy.quadrilateral.show(f)
    return


if __name__ == '__main__':
    test_show(0, 0)
