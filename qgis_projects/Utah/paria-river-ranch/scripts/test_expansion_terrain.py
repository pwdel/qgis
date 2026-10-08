import unittest
import numpy as np
from expansion_terrain import percent,nearby_lower
class TerrainTests(unittest.TestCase):
 def test_grades(self):
  for p in [30,45,60,90]:self.assertAlmostEqual(float(percent(np.degrees(np.arctan(p/100)))),p)
 def test_plane_drop(self):
  y,x=np.mgrid[:51,:51];z=x*2.0
  d=nearby_lower(z,np.ones(z.shape,bool),10,100)
  self.assertAlmostEqual(d[25,25],20)
 def test_missing_is_not_drop(self):
  z=np.ones((51,51))*2000;v=np.ones(z.shape,bool);v[25,26]=False
  d=nearby_lower(z,v,10,100)
  self.assertTrue(np.isnan(d[25,25]));self.assertTrue(np.isnan(d[0,0]))
 def test_flat(self):
  z=np.ones((51,51))*2000;d=nearby_lower(z,np.ones(z.shape,bool),10,100)
  self.assertEqual(d[25,25],0)
if __name__=='__main__':unittest.main()
