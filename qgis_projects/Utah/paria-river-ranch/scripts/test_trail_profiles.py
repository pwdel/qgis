"""Analytic checks: rise/fall, noisy level ground, gaps, and short components."""
import unittest
import numpy as np
from trail_profiles import elevation_metrics, smooth_segments

class ProfileTests(unittest.TestCase):
    def test_rise_and_fall(self):
        z=np.array([0.,10,20,10,0]);a,d=elevation_metrics(z,3)
        self.assertEqual((a,d),(20.,20.))
    def test_noisy_level(self):
        self.assertEqual(elevation_metrics(np.array([0.,1,-1,1,-1,0]),3),(0.,0.))
    def test_gap_never_bridged(self):
        self.assertEqual(elevation_metrics(np.array([0.,10,np.nan,100.,110.]),3),(20.,0.))
        s=smooth_segments(np.array([0.,10,np.nan,100.,110.]));self.assertTrue(np.isnan(s[2]))
        self.assertEqual(s[1],10);self.assertEqual(s[3],100)
    def test_descent_and_endpoints(self):
        self.assertEqual(elevation_metrics(np.array([20.,10,0]),3),(0.,20.))
        z=smooth_segments(np.array([0.,1,2,3,4]));self.assertEqual(z[0],0);self.assertEqual(z[-1],4)
    def test_empty_short(self):
        self.assertEqual(elevation_metrics(np.array([np.nan,5.,np.nan]),3),(0.,0.))
if __name__=='__main__':unittest.main()
