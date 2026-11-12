import uuid,redis
from fastapi import HTTPException
from src.models import NetworkRun,OutageScenario
from src.config.settings import REDIS_URL
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,scenario_id):
 if not db.get(OutageScenario,scenario_id):raise HTTPException(404,"推演不存在")
 item=NetworkRun(id=str(uuid.uuid4()),scenario_id=scenario_id,status="queued",result={},error="",created_at=now());db.add(item);db.commit()
 try:redis.Redis.from_url(REDIS_URL).lpush("transfer-resilience:jobs",item.id)
 except redis.RedisError:
  item.status="failed";item.error="后台队列不可用，请重试";db.commit();raise HTTPException(503,item.error)
 return serialize(item)
def require_completed(db,id):
 item=db.get(NetworkRun,id)
 if not item:raise HTTPException(404,"运行不存在")
 if item.status!="completed":raise HTTPException(409,"计算尚未完成")
 return item
