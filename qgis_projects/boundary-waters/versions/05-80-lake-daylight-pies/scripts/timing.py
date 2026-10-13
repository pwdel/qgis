"""Explicit teaching scenarios; distances are geographic kilometres."""
import math
ASSUMPTIONS={'paddle_kmh':[4.0,2.0],'loaded_walk_kmh':[3.0,2.0],'return_walk_kmh':[4.0,3.0],'handling_minutes':[10,20],'carry_traversals':[2,1],'rod_metres':5.0292,'windbound_waits_included':False,'scenario_not_prediction':True}
def distance(d):
 if not math.isfinite(d) or d<0:raise ValueError('Distance must be finite and nonnegative')
 return d
def paddle(d,detour_low=.15,detour_high=.35):
 distance(d)
 if not 0<=detour_low<=detour_high:raise ValueError('Invalid detour allowance')
 fast,slow=ASSUMPTIONS['paddle_kmh']
 return d*(1+detour_low)/fast,d*(1+detour_high)/slow
def carry(d):
 distance(d)
 lf,ls=ASSUMPTIONS['loaded_walk_kmh'];rf,rs=ASSUMPTIONS['return_walk_kmh'];hl,hh=ASSUMPTIONS['handling_minutes'];nl,nr=ASSUMPTIONS['carry_traversals']
 return nl*d/lf+nr*d/rf+hl/60,nl*d/ls+nr*d/rs+hh/60
def rounded(lo,hi):
 if not 0<=lo<=hi or not math.isfinite(hi):raise ValueError('Invalid time range')
 a=math.floor(lo*4+1e-10)/4;b=math.ceil(hi*4-1e-10)/4
 if hi>0:b=max(b,a+.25)
 return a,b
def hours(lo,hi):
 a,b=rounded(lo,hi)
 return f'{a:g}-{b:g} h'
