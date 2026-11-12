import math
def validate_network(node_ids,arcs,source,sink,disabled=()):
 if len(node_ids)<2 or len(set(node_ids))!=len(node_ids) or any(not isinstance(n,str) or not n for n in node_ids):raise ValueError("节点代码须为至少两个唯一非空字符串")
 if source not in node_ids or sink not in node_ids or source==sink:raise ValueError("源汇须不同且都在节点集合中")
 ids=[a["arc_id"] for a in arcs]
 if len(ids)!=len(set(ids)) or any(not isinstance(i,str) or not i for i in ids):raise ValueError("每条有向边必须保留唯一非空边ID")
 for a in arcs:
  if a["source"] not in node_ids or a["target"] not in node_ids:raise ValueError("边端点不在节点集合中")
  if not isinstance(a["capacity"],int) or isinstance(a["capacity"],bool) or a["capacity"]<0:raise ValueError("容量须非负整数")
  if not math.isfinite(a["travel_minutes"]) or a["travel_minutes"]<0:raise ValueError("时长须有限非负")
 blocked=set(disabled)
 if not blocked<=set(ids):raise ValueError("停用列表含未知边ID")
 return blocked
