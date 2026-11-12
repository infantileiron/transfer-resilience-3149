from fastapi import APIRouter,Depends
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import OutageScenario
from src.schemas.scenario import ScenarioInput
from src.services import scenarios as service
from src.utils.serialization import rows
router=APIRouter(prefix="/scenarios")
@router.get("")
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(OutageScenario).order_by(OutageScenario.created_at.desc())))
@router.post("")
def create(payload:ScenarioInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload)
