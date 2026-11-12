import json
from sqlalchemy import select,func
from src.config.database import Base,engine,Session
from src.models import User,NetworkDataset,TransferArc,OutageScenario,NetworkRun,ResilienceReview,Report
from src.services.analysis import analyze
from src.services.arcs import snapshot
from src.utils.security import hash_password
from src.utils.time import now
def seed():
 Base.metadata.create_all(engine)
 with Session() as db:
  for role in ("admin","analyst","viewer"):
   if not db.get(User,role):db.add(User(id=role,email=role+"@hengyuan.demo",password=hash_password("Network2026!"),role=role))
  nodes=[{"node_id":n,"label":label,"x":x,"y":y} for n,label,x,y in [("S","北岸集散",8,48),("A","东联站",27,20),("B","港西站",27,65),("C","铁路中转",45,8),("D","驳运中转",45,45),("E","拼箱中心",45,82),("F","北站",65,20),("G","南站",65,65),("H","外联枢纽",82,40),("T","终到枢纽",94,72)]]
  raw=[("S","A",8,6),("S","B",6,9),("A","C",5,4),("A","D",5,5),("B","D",5,3),("B","E",4,5),("C","F",5,7),("D","F",4,4),("D","G",5,6),("E","G",4,3),("F","H",6,5),("G","H",6,4),("H","T",10,6),("F","T",3,12),("G","T",3,10),("A","B",2,2),("D","E",2,2),("C","D",2,1),("S","A",3,7),("D","A",2,3),("H","G",1,5),("B","A",1,4)]
  if not db.get(NetworkDataset,"demo-data"):db.add(NetworkDataset(id="demo-data",name="衡远模拟联运·10枢纽22弧",source="hengyuan_transfer_202611.json",nodes=nodes,created_at=now()));db.flush()
  for i,(u,v,cap,minutes) in enumerate(raw,1):
   id=f"demo-arc-{i}"
   if not db.get(TransferArc,id):db.add(TransferArc(id=id,dataset_id="demo-data",arc_id=f"e{i:02}",source=u,target=v,capacity=cap,travel_minutes=minutes,created_at=now()))
  db.flush();arcs=snapshot(db,"demo-data")
  definitions=[("demo-baseline","无停用·基准核对",[]),("demo-outage","停用e13·外联瓶颈对照",["e13"]),("demo-disconnected","源站出弧全停·断连反例",["e01","e02","e19"])]
  for id,name,disabled in definitions:
   if not db.get(OutageScenario,id):db.add(OutageScenario(id=id,name=name,dataset_id="demo-data",source_node="S",sink_node="T",disabled_arc_ids=disabled,arc_snapshot=arcs,created_at=now()))
  db.flush()
  if not db.get(NetworkRun,"demo-run"):db.add(NetworkRun(id="demo-run",scenario_id="demo-outage",status="completed",result=analyze(db.get(NetworkDataset,"demo-data"),db.get(OutageScenario,"demo-outage")),error="",created_at=now()));db.flush()
  if not db.get(ResilienceReview,"demo-review"):db.add(ResilienceReview(id="demo-review",run_id="demo-run",note="每条边独立保留ID，逐边容量界与节点守恒通过，最大流等于割容量。最短时长路径是独立指标，不解释为最大流分配。",decision="accepted",author="analyst@hengyuan.demo",created_at=now()));db.flush()
  if not db.get(Report,"demo-report"):db.add(Report(id="demo-report",run_id="demo-run",title="衡远模拟中转·停边韧性复核",published_by="admin@hengyuan.demo",created_at=now()))
  db.commit();return {m.__tablename__:db.scalar(select(func.count()).select_from(m)) for m in (User,NetworkDataset,TransferArc,OutageScenario,NetworkRun,ResilienceReview,Report)}
if __name__=="__main__":print(json.dumps(seed(),ensure_ascii=False))
