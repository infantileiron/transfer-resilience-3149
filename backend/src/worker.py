from pathlib import Path
import redis,traceback
from sqlalchemy import select
from src.config.settings import REDIS_URL
from src.config.database import Session
from src.models import NetworkRun,OutageScenario,NetworkDataset
from src.services.analysis import analyze
client=redis.Redis.from_url(REDIS_URL);heartbeat=Path("/artifacts/worker-heartbeat")
def execute(id):
 with Session() as db:
  run=db.get(NetworkRun,id)
  if not run or run.status not in ("queued","running"):return
  run.status="running";db.commit()
  try:
   scenario=db.get(OutageScenario,run.scenario_id);dataset=db.get(NetworkDataset,scenario.dataset_id)
   run.result=analyze(dataset,scenario);run.status="completed"
  except Exception as e:run.error=str(e);run.status="failed";traceback.print_exc()
  db.commit()
with Session() as db:
 for id in db.scalars(select(NetworkRun.id).where(NetworkRun.status.in_(["queued","running"]))):client.lpush("transfer-resilience:jobs",id)
while True:
 heartbeat.touch();job=client.brpop("transfer-resilience:jobs",timeout=1)
 if job:execute(job[1].decode())
