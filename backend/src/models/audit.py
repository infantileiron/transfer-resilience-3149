from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class AuditEvent(Base):
 __tablename__="audit_events"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 actor:Mapped[str]=mapped_column(String(160))
 action:Mapped[str]=mapped_column(String(255))
 status:Mapped[int]=mapped_column(Integer)
 created_at:Mapped[str]=mapped_column(String(64))
