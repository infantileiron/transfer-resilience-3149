from fastapi import APIRouter,Depends,HTTPException
from src.config.database import db_session
from src.controllers.auth import current_user,admin
from src.models import Report,ResilienceReview
from src.schemas.report import ReportInput
from src.services import reports as service
from src.utils.serialization import serialize
router=APIRouter(prefix="/reports")
@router.get("")
def listing(db=Depends(db_session),user=Depends(current_user)):return service.versions(db)
@router.post("")
def create(payload:ReportInput,db=Depends(db_session),user=Depends(admin)):return service.create(db,payload,user)
@router.get("/runs/{run_id}/versions")
def run_versions(run_id:str,db=Depends(db_session),user=Depends(current_user)):return {"run_id":run_id,"versions":service.versions(db,run_id)}
@router.get("/{id}/versions")
def report_versions(id:str,db=Depends(db_session),user=Depends(current_user)):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,"报告不存在")
 return {"run_id":report.run_id,"versions":service.versions(db,report.run_id)}
@router.get("/{id}")
def detail(id:str,db=Depends(db_session),user=Depends(current_user)):
 report=db.get(Report,id)
 if not report:raise HTTPException(404,"报告不存在")
 data=serialize(report)
 data["has_snapshot"]=bool(report.snapshot)
 data["review"]=serialize(db.get(ResilienceReview,report.review_id)) if report.review_id else None
 return data
@router.get("/{id}/csv")
def download(id:str,db=Depends(db_session),user=Depends(current_user)):
 from fastapi.responses import Response
 report=db.get(Report,id)
 if not report:raise HTTPException(404,"报告不存在")
 headers={"Content-Disposition":f"attachment; filename=transfer-resilience-v{report.version}.csv"}
 headers.update(service.invalid_headers(report))
 return Response(service.export(db,id),media_type="text/csv; charset=utf-8",headers=headers)
