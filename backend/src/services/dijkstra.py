import heapq,math
from src.services.validation import validate_network
def shortest_path(node_ids,arcs,source,sink,disabled=()):
 blocked=validate_network(node_ids,arcs,source,sink,disabled);adjacency={n:[] for n in node_ids}
 for a in sorted(arcs,key=lambda a:a["arc_id"]):
  if a["capacity"]>0 and a["arc_id"] not in blocked:adjacency[a["source"]].append(a)
 distance={n:math.inf for n in node_ids};distance[source]=0.0;parent={};queue=[(0.0,source)]
 while queue:
  current,u=heapq.heappop(queue)
  if current>distance[u]:continue
  if u==sink:break
  for arc in adjacency[u]:
   v=arc["target"];candidate=current+arc["travel_minutes"]
   if candidate<distance[v]:distance[v]=candidate;parent[v]=(u,arc["arc_id"]);heapq.heappush(queue,(candidate,v))
 if not math.isfinite(distance[sink]):return {"reachable":False,"minutes":None,"node_path":[],"arc_path":[]}
 nodes=[sink];path=[];current=sink
 while current!=source:
  previous,arc_id=parent[current];path.append(arc_id);nodes.append(previous);current=previous
 return {"reachable":True,"minutes":distance[sink],"node_path":nodes[::-1],"arc_path":path[::-1]}
