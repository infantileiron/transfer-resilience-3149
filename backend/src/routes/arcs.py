from fastapi import APIRouter,Depends
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import TransferArc
from src.schemas.arc import ArcInput
from src.services import arcs as service
from src.utils.serialization import rows
router=APIRouter(prefix="/arcs")
@router.get("")
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(TransferArc).order_by(TransferArc.created_at.desc())))
@router.post("")
def create(payload:ArcInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload)
