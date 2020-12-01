"""Unittests for the functions in svid_location, using the true data from 2020-02-11."""

import unittest
from algorithms.FPL import *
import numpy.testing as npt
import pandas.testing as pt
from itertools import product
import numpy as np
import math

class TestFPL(unittest.TestCase):
    def setUp(self) -> None:
        self.fpl = FourParamLogisticRegression()
        self.fpl.a, self.fpl.b, self.fpl.c, self.fpl.d = 0.95, 1, 1, 0.05
        self.batch_size=3

    def test_four_param_sigmoid(self) -> None:
        self.assertAlmostEqual(self.fpl.four_param_sigmoid(1),0.5)
        self.assertAlmostEqual(self.fpl.four_param_sigmoid(1e6),0.95)
        self.assertAlmostEqual(self.fpl.four_param_sigmoid(-1e6),0.05)
        self.assertAlmostEqual(self.fpl.four_param_sigmoid(2),0.05+0.9/(1+math.exp(-1)))

    def test_batch_update(self) -> None:
        xhat=np.array((1,1))
        ytrue=np.array((0,0))
        # y_fac=2
        # delta_a =  1
        # delta_b = 0
        # delta_c = -0.45 
        # delta_d = 1
        a,b,c,d =0.95 -self.fpl.lr[0], 1, 1+0.45*self.fpl.lr[2], 0.05 -self.fpl.lr[3]
        self.fpl.batch_update(xhat,ytrue)
        self.assertAlmostEqual(self.fpl.a,a)
        self.assertAlmostEqual(self.fpl.b,b)
        self.assertAlmostEqual(self.fpl.c,c)
        self.assertAlmostEqual(self.fpl.d,d)


    def test_fit_online(self) -> None:
        X=np.arange(10)
        Y=np.array([1]*10)
        p=self.fpl.fit_online(X,Y)
        self.assertEqual(len(p),10)
        self.assertEqual(len(p[9]),4)
        npt.assert_almost_equal(p[9],[self.fpl.a,self.fpl.b,self.fpl.c,self.fpl.d])
        updates = max(max([abs(i-j) for i,j in zip(p[n],p[n+1])] for n in range(9) if n not in {2,5,8,9}))
        self.assertAlmostEqual(updates,0)

    def test_fit_offline(self) -> None:
        X=np.arange(-20,20)
        Y=np.array([1,0]*20)
        np.random.shuffle(Y)

        self.fpl.fit_offline(X,Y)

        theta=[self.fpl.a,self.fpl.b,self.fpl.c,self.fpl.d]

        def neg_log_likelihood(theta, X, y):
            m = X.shape[0]
            denom_ = 1 + np.exp( - theta[1] * (X - theta[2]) )
            yhat = theta[3] + (theta[0] - theta[3])/denom_
            return -(1 / m) * np.sum(y*np.log(yhat) + (1 - y)*np.log(1 - yhat))

        min_ = neg_log_likelihood(theta,X,Y)

        A = np.arange(0.5+1e-3,1 - 1e-3,0.1)
        B = np.arange(1e-2,5,1)
        C =np.arange(1e-3,20,1)
        D =np.arange(0+1e-3,0.5-1e-3,0.1)

        likelihoods = [neg_log_likelihood([a,b,c,d],X,Y) for a,b,c,d in product(A,B,C,D) ]
        self.assertLessEqual(min_,min(likelihoods))

        

    def test_prob(self) -> None:
        X=np.array([np.nan,1])
        npt.assert_almost_equal(self.fpl.prob(X),np.array([0,0.5]))

    def test_pred(self) -> None:
        X=np.array([np.nan,1.001])
        npt.assert_almost_equal(self.fpl.predict(X),np.array([0,1]))

if __name__ == '__main__':
    unittest.main()




