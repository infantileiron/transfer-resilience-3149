import uuid,csv,io
from sqlalchemy import select,or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.models import Report,ResilienceReview,NetworkRun
from src.utils.time import now
from src.utils.serialization import serialize
from src.utils.csv import safe_cell

def _latest_review(db,run_id,lock=False):
 query=select(ResilienceReview).where(ResilienceReview.run_id==run_id).order_by(ResilienceReview.created_at.desc(),ResilienceReview.id.desc())
 if lock:query=query.with_for_update()
 return db.scalar(query)

def _lock_run(db,run_id):
 return db.scalar(select(NetworkRun).where(NetworkRun.id==run_id).with_for_update())

def snapshot_of(run,review):
 result=run.result or {}
 return {"run_id":run.id,"scenario_id":run.scenario_id,"checksum":result.get("checksum",""),"review_id":review.id,"review_note":review.note,"review_author":review.author,"review_created_at":review.created_at,"source":result.get("source"),"sink":result.get("sink"),"disabled_arc_ids":result.get("disabled_arc_ids",[]),"baseline":result.get("baseline"),"outage":result.get("outage"),"impact":result.get("impact")}

def _reason(review,kind="review"):
 stamp=now()
 if kind=="replaced":text="出现新的接受复核意见，旧归档版本已被取代，需按新版本重新归档。"
 elif review.decision=="needs_attention":
  detail=review.note.strip()
  if len(detail)>160:detail=detail[:160]+"…"
  text=f"复核意见「需要继续核查」推翻了先前的接受结论：{detail}"
 else:text="出现新的接受复核意见，旧归档版本已被取代，需按新版本重新归档。"
 return stamp,text

def invalidate(db,review,commit=True,kind="review"):
 """Mark valid reports that no longer match the current review invalid.
 A needs_attention opinion invalidates every valid archive of the run."""
 conditions=[Report.run_id==review.run_id,Report.status=="valid"]
 if review.decision=="accepted":conditions.append(or_(Report.review_id.is_(None),Report.review_id!=review.id))
 target=db.scalars(select(Report).where(*conditions).with_for_update()).all()
 stamp,text=_reason(review,kind)
 for item in target:
  item.status="invalid";item.invalidated_at=stamp;item.invalidated_by=review.author;item.invalidated_reason=text;item.invalidated_review_id=review.id
 if commit:db.commit()
 return target

def enforce_single_valid(db,run_id):
 """Concurrency backstop: at most one valid version per run, bound to the
 latest accepted review. Runs in its own transaction after the main commit,
 so an interleaved archive/review cannot leave a stale valid version."""
 db.expire_all()
 latest=_latest_review(db,run_id)
 keep=latest.id if latest and latest.decision=="accepted" else None
 reports=db.scalars(select(Report).where(Report.run_id==run_id,Report.status=="valid").with_for_update()).all()
 changed=False
 for item in reports:
  if item.review_id==keep:continue
  item.status="invalid";item.invalidated_at=now();item.invalidated_by=latest.author if latest else "system"
  item.invalidated_review_id=latest.id if latest else ""
  item.invalidated_reason=(_reason(latest,kind="replaced")[1] if latest else "最新复核意见不是接受，归档结论失效。")
  changed=True
 if changed:db.commit()
 return changed

def validate_snapshot(run,review):
 result=run.result or {}
 if not result.get("baseline") or not result.get("outage"):raise HTTPException(409,"推演结果不完整，不能归档")
 checks=(result.get("baseline",{}).get("max_flow",{}).get("checks")) or {}
 if checks and not all(checks.values()):raise HTTPException(409,"推演证据检查未通过，不能归档")

def create(db,payload,user):
 # Lock the run row first; reviews lock in the same order, avoiding deadlock.
 run=_lock_run(db,payload.run_id)
 if not run:raise HTTPException(404,"运行不存在")
 if run.status!="completed":raise HTTPException(409,"计算尚未完成")
 latest=_latest_review(db,run.id,lock=True)
 if not latest or latest.decision!="accepted":raise HTTPException(409,"最新韧性复核须为接受后才能归档")
 if payload.review_id and payload.review_id!=latest.id:raise HTTPException(409,"归档须绑定最新的接受复核意见")
 # Same accepted review archived twice returns the original version, no new version.
 existing=db.scalar(select(Report).where(Report.run_id==run.id,Report.review_id==latest.id))
 if existing:return _public(existing)
 validate_snapshot(run,latest)
 invalidate(db,latest,commit=False,kind="replaced")
 previous=db.scalar(select(Report).where(Report.run_id==run.id).order_by(Report.version.desc()))
 version=(previous.version+1) if previous else 1
 item=Report(id=str(uuid.uuid4()),run_id=run.id,review_id=latest.id,version=version,status="valid",title=payload.title,published_by=user["email"],created_at=now(),accepted_note=latest.note,accepted_author=latest.author,result_checksum=(run.result or {}).get("checksum",""),snapshot=snapshot_of(run,latest),invalidated_at="",invalidated_by="",invalidated_reason="",invalidated_review_id="")
 db.add(item)
 try:db.commit()
 except IntegrityError:
  db.rollback()
  concurrent=db.scalar(select(Report).where(Report.run_id==run.id,Report.review_id==latest.id))
  if concurrent:return _public(concurrent)
  raise HTTPException(409,"本次推演归档发生并发冲突，请重试")
 # Reconcile with a review that committed while this archive was in flight:
 # never leave a valid version whose accepted review has already been superseded.
 db.expire_all()
 current=_latest_review(db,run.id)
 if item.status=="valid" and (not current or current.id!=latest.id or current.decision!="accepted"):
  item.status="invalid";item.invalidated_at=now();item.invalidated_by=current.author if current else user["email"];item.invalidated_review_id=current.id if current else ""
  item.invalidated_reason="归档期间出现新的复核意见，本版本未生效，需按最新接受意见重新归档。"
  db.commit()
  raise HTTPException(409,"复核状态在归档期间发生变化，本次归档已标记失效")
 db.expire_all();enforce_single_valid(db,run.id)
 db.expire_all();item=db.get(Report,item.id)
 return _public(item)

def _public(report):
 data=serialize(report);data.pop("snapshot",None);data["has_snapshot"]=bool(report.snapshot)
 data["summary"]=_summary(report.snapshot or {})
 return data

def _summary(snapshot):
 if not snapshot.get("baseline") or not snapshot.get("outage"):return None
 before=snapshot["baseline"];after=snapshot["outage"]
 return {"baseline_maxflow":before["max_flow"]["value"],"outage_maxflow":after["max_flow"]["value"],"cut_capacity":after["max_flow"]["cut_capacity"],"flow_reduction":(snapshot.get("impact") or {}).get("flow_reduction"),"outage_shortest_minutes":after["shortest"]["minutes"],"outage_reachable":after["shortest"]["reachable"]}

def versions(db,run_id=None):
 query=select(Report).order_by(Report.created_at.desc(),Report.version.desc()) if run_id is None else select(Report).where(Report.run_id==run_id).order_by(Report.version)
 return [_public(r) for r in db.scalars(query)]

def invalid_headers(report):
 if report.status=="valid":return {}
 from urllib.parse import quote
 reason=quote(report.invalidated_reason or "归档结论已失效",safe="")
 return {"X-Report-Status":"invalid","X-Report-Reason":reason}

def _report_result(db,report):
 snapshot=report.snapshot or {}
 if snapshot.get("baseline") is not None and snapshot.get("outage") is not None:return snapshot
 run=db.get(NetworkRun,report.run_id)
 if not run or run.status!="completed":raise HTTPException(409,"报告对应的推演结果已不可用")
 return run.result

def export(db,id):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,"报告不存在")
 result=_report_result(db,report)
 buf=io.StringIO();cols=["phase","arc_id","source","target","capacity","effective_capacity","flow","residual_forward","residual_reverse","disabled","in_cut","on_shortest","maxflow","cut_capacity","shortest_reachable","shortest_minutes","shortest_arc_path"]
 writer=csv.DictWriter(buf,cols);writer.writeheader()
 if report.status!="valid":
  writer.writerow({"phase":"report_status","arc_id":report.id,"source":report.status,"target":report.invalidated_at,"capacity":report.invalidated_by,"effective_capacity":"","flow":"","residual_forward":"","residual_reverse":"","disabled":"","in_cut":"","on_shortest":"","maxflow":"","cut_capacity":"","shortest_reachable":"","shortest_minutes":"","shortest_arc_path":report.invalidated_reason})
 for phase in ("baseline","outage"):
  data=result[phase];flow=data["max_flow"];path=data["shortest"];cut={a["arc_id"] for a in flow["cut_arcs"]};meta={"phase":phase,"maxflow":flow["value"],"cut_capacity":flow["cut_capacity"],"shortest_reachable":path["reachable"],"shortest_minutes":path["minutes"],"shortest_arc_path":" > ".join(path["arc_path"])}
  for arc in flow["arc_flows"]:writer.writerow({**meta,**{k:safe_cell(arc[k]) for k in cols[1:10]},"in_cut":arc["arc_id"] in cut,"on_shortest":arc["arc_id"] in path["arc_path"]})
  if not flow["arc_flows"]:writer.writerow(meta)
 return "﻿"+buf.getvalue()
