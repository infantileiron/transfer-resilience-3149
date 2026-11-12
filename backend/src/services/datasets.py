import uuid,math
from fastapi import HTTPException
from sqlalchemy import select
from src.models import NetworkDataset,TransferArc
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 if db.scalar(select(NetworkDataset).where(NetworkDataset.name==payload.name)):raise HTTPException(409,"网络名称已存在")
 nodes=[n.model_dump() for n in payload.nodes]
 for i,n in enumerate(nodes):
  angle=2*math.pi*i/len(nodes)
  if n["x"] is None:n["x"]=50+40*math.cos(angle)
  if n["y"] is None:n["y"]=50+38*math.sin(angle)
 item=NetworkDataset(id=str(uuid.uuid4()),name=payload.name,source=payload.source,nodes=nodes,created_at=now());db.add(item);db.flush()
 for arc in payload.arcs:db.add(TransferArc(id=str(uuid.uuid4()),dataset_id=item.id,created_at=now(),**arc.model_dump()))
 db.commit();return serialize(item)
def require(db,id):
 item=db.get(NetworkDataset,id)
 if not item:raise HTTPException(404,"网络不存在")
 return item
