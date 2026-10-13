"""Water-contained path builder reused from the geographic teaching chart."""
import heapq,math,numpy as np,shapely
from shapely.geometry import Point,LineString
def waterpath(w,start,end,step=25):
 allowed=w.buffer(2)
 if allowed.covers(LineString([start,end])):return LineString([start,end])
 xmin,ymin,xmax,ymax=w.bounds
 xs=np.arange(xmin+step/2,xmax,step);ys=np.arange(ymin+step/2,ymax,step)
 xx,yy=np.meshgrid(xs,ys);mask=shapely.contains_xy(w,xx,yy);rr,cc=np.where(mask)
 centers=np.column_stack([xs[cc],ys[rr]])
 def endpoint(p):
  ids=np.argsort(np.sum((centers-np.array(p.coords[0]))**2,axis=1))[:160]
  for idx in ids:
   q=Point(centers[idx])
   if allowed.covers(LineString([p,q])):return int(rr[idx]),int(cc[idx])
  raise ValueError('No water access from '+p.wkt)
 s=endpoint(start);goal=endpoint(end);heap=[(0,0,s)];dist={s:0};prev={};done=set()
 while heap:
  _,cost,u=heapq.heappop(heap)
  if u in done:continue
  if u==goal:break
  done.add(u);r,c=u
  for dr,dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
   v=(r+dr,c+dc);nr,nc=v
   if not (0<=nr<len(ys) and 0<=nc<len(xs) and mask[nr,nc]):continue
   new=cost+math.hypot(dr,dc)*step
   if new>=dist.get(v,float('inf')):continue
   if not allowed.covers(LineString([(xs[c],ys[r]),(xs[nc],ys[nr])])):continue
   dist[v]=new;prev[v]=u;h=math.hypot(nr-goal[0],nc-goal[1])*step;heapq.heappush(heap,(new+h,new,v))
 assert goal in dist,'No water route'
 nodes=[goal]
 while nodes[-1]!=s:nodes.append(prev[nodes[-1]])
 nodes.reverse();pts=[start]+[Point(xs[c],ys[r]) for r,c in nodes]+[end]
 # Greedy visible shortcuts preserve islands and peninsulas.
 out=[pts[0]];i=0
 while i<len(pts)-1:
  j=len(pts)-1
  while j>i+1 and not allowed.covers(LineString([pts[i],pts[j]])):j-=1
  out.append(pts[j]);i=j
 line=LineString(out);assert allowed.covers(line)
 return line
