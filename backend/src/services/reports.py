import uuid,csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import Report,ResilienceReview
from src.services.runs import require_completed
from src.utils.time import now
from src.utils.serialization import serialize
from src.utils.csv import safe_cell
def create(db,payload,user):
 require_completed(db,payload.run_id)
 review=db.scalar(select(ResilienceReview).where(ResilienceReview.run_id==payload.run_id).order_by(ResilienceReview.created_at.desc()))
 if not review or review.decision!="accepted":raise HTTPException(409,"最新韧性复核须为接受后才能归档")
 if db.scalar(select(Report).where(Report.run_id==payload.run_id)):raise HTTPException(409,"本次推演已归档")
 item=Report(id=str(uuid.uuid4()),published_by=user["email"],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,"报告不存在")
 result=require_completed(db,report.run_id).result;buf=io.StringIO();cols=["phase","arc_id","source","target","capacity","effective_capacity","flow","residual_forward","residual_reverse","disabled","in_cut","on_shortest","maxflow","cut_capacity","shortest_reachable","shortest_minutes","shortest_arc_path"]
 writer=csv.DictWriter(buf,cols);writer.writeheader()
 for phase in ("baseline","outage"):
  data=result[phase];flow=data["max_flow"];path=data["shortest"];cut={a["arc_id"] for a in flow["cut_arcs"]};meta={"phase":phase,"maxflow":flow["value"],"cut_capacity":flow["cut_capacity"],"shortest_reachable":path["reachable"],"shortest_minutes":path["minutes"],"shortest_arc_path":" > ".join(path["arc_path"])}
  for arc in flow["arc_flows"]:writer.writerow({**meta,**{k:safe_cell(arc[k]) for k in cols[1:10]},"in_cut":arc["arc_id"] in cut,"on_shortest":arc["arc_id"] in path["arc_path"]})
  if not flow["arc_flows"]:writer.writerow(meta)
 return "\ufeff"+buf.getvalue()
