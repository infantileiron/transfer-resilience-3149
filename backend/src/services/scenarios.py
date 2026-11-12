import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import OutageScenario
from src.services.datasets import require
from src.services.arcs import snapshot
from src.services.validation import validate_network
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 dataset=require(db,payload.dataset_id);arcs=snapshot(db,payload.dataset_id)
 try:validate_network([n["node_id"] for n in dataset.nodes],arcs,payload.source_node,payload.sink_node,payload.disabled_arc_ids)
 except ValueError as e:raise HTTPException(422,str(e))
 if db.scalar(select(OutageScenario).where(OutageScenario.name==payload.name)):raise HTTPException(409,"推演名称已存在")
 item=OutageScenario(id=str(uuid.uuid4()),arc_snapshot=arcs,created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
