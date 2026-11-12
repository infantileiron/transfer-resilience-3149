from collections import deque
from src.services.validation import validate_network
def edmonds_karp(node_ids,arcs,source,sink,disabled=()):
 blocked=validate_network(node_ids,arcs,source,sink,disabled);ordered=sorted(arcs,key=lambda a:a["arc_id"])
 adjacency={n:[] for n in node_ids};residual=[];flows={a["arc_id"]:0 for a in ordered}
 # Every original edge owns one independent forward/reverse pair by global index.
 # Parallel and antiparallel edges never overwrite each other's residual capacity.
 for a in ordered:
  capacity=0 if a["arc_id"] in blocked else a["capacity"];forward=len(residual);reverse=forward+1
  residual.append({"u":a["source"],"v":a["target"],"capacity":capacity,"reverse":reverse,"arc_id":a["arc_id"],"sign":1})
  residual.append({"u":a["target"],"v":a["source"],"capacity":0,"reverse":forward,"arc_id":a["arc_id"],"sign":-1})
  adjacency[a["source"]].append(forward);adjacency[a["target"]].append(reverse)
 value=0;augmentations=[]
 while True:
  parent={source:None};queue=deque([source])
  while queue and sink not in parent:
   u=queue.popleft()
   for index in adjacency[u]:
    edge=residual[index]
    if edge["capacity"]>0 and edge["v"] not in parent:
     parent[edge["v"]]=index;queue.append(edge["v"])
     if edge["v"]==sink:break
  if sink not in parent:break
  path=[];node=sink
  while node!=source:
   index=parent[node];path.append(index);node=residual[index]["u"]
  path.reverse();delta=min(residual[i]["capacity"] for i in path)
  steps=[]
  for index in path:
   edge=residual[index];edge["capacity"]-=delta;residual[edge["reverse"]]["capacity"]+=delta;flows[edge["arc_id"]]+=edge["sign"]*delta
   steps.append({"arc_id":edge["arc_id"],"direction":edge["sign"],"source":edge["u"],"target":edge["v"]})
  value+=delta;augmentations.append({"amount":delta,"steps":steps})
 reachable={source};queue=deque([source])
 while queue:
  u=queue.popleft()
  for index in adjacency[u]:
   edge=residual[index]
   if edge["capacity"]>0 and edge["v"] not in reachable:reachable.add(edge["v"]);queue.append(edge["v"])
 rows=[];cut=[]
 for a in ordered:
  capacity=0 if a["arc_id"] in blocked else a["capacity"];flow=flows[a["arc_id"]]
  row={**a,"effective_capacity":capacity,"flow":flow,"residual_forward":capacity-flow,"residual_reverse":flow,"disabled":a["arc_id"] in blocked}
  rows.append(row)
  if a["source"] in reachable and a["target"] not in reachable:cut.append(row)
 cut_capacity=sum(a["effective_capacity"] for a in cut);conservation=[]
 for n in node_ids:
  incoming=sum(r["flow"] for r in rows if r["target"]==n);outgoing=sum(r["flow"] for r in rows if r["source"]==n)
  expected=value if n==source else -value if n==sink else 0
  conservation.append({"node_id":n,"inflow":incoming,"outflow":outgoing,"balance":outgoing-incoming,"expected_balance":expected,"conserved":outgoing-incoming==expected})
 checks={"flow_capacity_bounds":all(0<=r["flow"]<=r["effective_capacity"] for r in rows),"conservation":all(r["conserved"] for r in conservation),"maxflow_equals_mincut":value==cut_capacity,"sink_not_residual_reachable":sink not in reachable}
 if not all(checks.values()):raise ValueError("最大流证据检查失败，未输出可信结论")
 return {"value":value,"cut_capacity":cut_capacity,"source_side":sorted(reachable),"sink_side":sorted(set(node_ids)-reachable),"cut_arcs":cut,"arc_flows":rows,"conservation":conservation,"checks":checks,"augmentations":augmentations,"residual_edge_count":len(residual)}
