import uuid
from fastapi import HTTPException
from sqlalchemy import select,func
from src.models import TransferArc
from src.services.datasets import require
from src.utils.time import now
from src.utils.serialization import serialize
def snapshot(db,dataset_id):
 arcs=list(db.scalars(select(TransferArc).where(TransferArc.dataset_id==dataset_id).order_by(TransferArc.arc_id)))
 return [{k:getattr(a,k) for k in ("arc_id","source","target","capacity","travel_minutes")} for a in arcs]
def create(db,payload):
 dataset=require(db,payload.dataset_id);ids={n["node_id"] for n in dataset.nodes}
 if payload.source not in ids or payload.target not in ids:raise HTTPException(422,"边端点不在所选网络中")
 if db.scalar(select(TransferArc).where(TransferArc.dataset_id==payload.dataset_id,TransferArc.arc_id==payload.arc_id)):raise HTTPException(409,"该网络已有此边ID，平行边也必须使用新ID")
 if db.scalar(select(func.count()).select_from(TransferArc).where(TransferArc.dataset_id==payload.dataset_id))>=200:raise HTTPException(422,"每网络最多200条边")
 item=TransferArc(id=str(uuid.uuid4()),created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
