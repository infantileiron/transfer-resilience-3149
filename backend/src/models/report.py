from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class Report(Base):
 __tablename__="network_reports"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("network_runs.id"),unique=True)
 title:Mapped[str]=mapped_column(String(160))
 published_by:Mapped[str]=mapped_column(String(160))
 created_at:Mapped[str]=mapped_column(String(64))
