import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
try:
 import timing
except ModuleNotFoundError:
 timing=None
class TimingTests(unittest.TestCase):
 def test_available(self): self.assertIsNotNone(timing,'Timing model must exist')
 @unittest.skipIf(timing is None,'Model not implemented yet')
 def test_double_carry(self):
  lo,hi=timing.carry(1)
  self.assertAlmostEqual(lo,65/60)
  self.assertAlmostEqual(hi,100/60)
 @unittest.skipIf(timing is None,'Model not implemented yet')
 def test_indirect_paddle(self):
  self.assertEqual(timing.paddle(4,.15,.35),(1.15,2.7))
 @unittest.skipIf(timing is None,'Model not implemented yet')
 def test_rounding_encloses(self):
  for lo,hi in [(1.15,2.7),(.01,.04),(2,2),(0,0)]:
   a,b=timing.rounded(lo,hi)
   self.assertLessEqual(a,lo);self.assertGreaterEqual(b,hi)
   if hi>0:self.assertGreaterEqual(b-a,.25)
 @unittest.skipIf(timing is None,'Model not implemented yet')
 def test_editable_assumptions(self):
  old=timing.ASSUMPTIONS['loaded_walk_kmh']
  try:
   timing.ASSUMPTIONS['loaded_walk_kmh']=[6,4]
   lo,hi=timing.carry(1)
   self.assertAlmostEqual(lo,.75);self.assertAlmostEqual(hi,7/6)
  finally:timing.ASSUMPTIONS['loaded_walk_kmh']=old
 @unittest.skipIf(timing is None,'Model not implemented yet')
 def test_invalid_distance(self):
  for value in [-1,float('nan'),float('inf')]:
   with self.assertRaises(ValueError): timing.carry(value)
if __name__=='__main__':unittest.main()
