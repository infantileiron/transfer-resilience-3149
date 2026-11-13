import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import ResilienceReview,NetworkRun
from src.utils.time import now
from src.utils.serialization import serialize
_DECISIONS=("accepted","needs_attention")
def create(db,payload,user):
 if payload.decision not in _DECISIONS:raise HTTPException(422,"复核判断必须为接受或需要继续核查")
 # Lock the run first (same order as archiving) so concurrent review/archive serializes.
 run=db.scalar(select(NetworkRun).where(NetworkRun.id==payload.run_id).with_for_update())
 if not run:raise HTTPException(404,"运行不存在")
 if run.status!="completed":raise HTTPException(409,"计算尚未完成")
 item=ResilienceReview(id=str(uuid.uuid4()),created_at=now(),author=user["email"],**payload.model_dump());db.add(item);db.flush()
 from src.services.reports import invalidate,enforce_single_valid
 invalidate(db,item,commit=False)
 db.commit()
 # Backstop in a fresh transaction: an archive may have committed between our
 # read and commit, and no stale valid version may survive it.
 enforce_single_valid(db,item.run_id)
 return serialize(item)
