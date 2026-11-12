import hashlib,json
from src.services.maxflow import edmonds_karp
from src.services.dijkstra import shortest_path
def analyze(dataset,scenario):
 ids=[n["node_id"] for n in dataset.nodes];arcs=scenario.arc_snapshot
 before={"max_flow":edmonds_karp(ids,arcs,scenario.source_node,scenario.sink_node),"shortest":shortest_path(ids,arcs,scenario.source_node,scenario.sink_node)}
 after={"max_flow":edmonds_karp(ids,arcs,scenario.source_node,scenario.sink_node,scenario.disabled_arc_ids),"shortest":shortest_path(ids,arcs,scenario.source_node,scenario.sink_node,scenario.disabled_arc_ids)}
 both=before["shortest"]["reachable"] and after["shortest"]["reachable"]
 return {"nodes":dataset.nodes,"arcs":arcs,"source":scenario.source_node,"sink":scenario.sink_node,"disabled_arc_ids":scenario.disabled_arc_ids,"baseline":before,"outage":after,"impact":{"flow_reduction":before["max_flow"]["value"]-after["max_flow"]["value"],"shortest_time_change_minutes":after["shortest"]["minutes"]-before["shortest"]["minutes"] if both else None,"lost_reachability":before["shortest"]["reachable"] and not after["shortest"]["reachable"]},"checksum":hashlib.sha256(json.dumps({"nodes":dataset.nodes,"arcs":arcs,"source":scenario.source_node,"sink":scenario.sink_node,"disabled":scenario.disabled_arc_ids},sort_keys=True).encode()).hexdigest(),"assumptions":["容量为非负整数箱/小时，时长为非负分钟；所有网络和节点位置为模拟，布局坐标不代表地理位置。","最大流使用Edmonds–Karp，每个原始边ID独立持有正/反残量对，平行和反向边不合并；逐边界限、逐节点守恒和maxflow=mincut均输出证据。","最短路使用Dijkstra，仅启用且正容量边可通行；零时长正容量路径可以合法返回0分钟，不可达返回null而不是伪0。","最大流分配不等于最短时长路径，也没有求最小费用流；不能把一条最短路当作全部最大流的走向。","推演建立时锁定边快照，停用前后用同一份容量与时长；后续新增边需新建推演，不改写已有证据。"]}
