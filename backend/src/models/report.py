from sqlalchemy import String,JSON,ForeignKey,Text,Integer,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class Report(Base):
 __tablename__="network_reports"
 __table_args__=(UniqueConstraint("run_id","version",name="uq_network_reports_run_version"),)
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("network_runs.id"))
 review_id:Mapped[str]=mapped_column(ForeignKey("resilience_reviews.id"),unique=True)
 version:Mapped[int]=mapped_column(Integer,default=1)
 title:Mapped[str]=mapped_column(String(160))
 published_by:Mapped[str]=mapped_column(String(160))
 created_at:Mapped[str]=mapped_column(String(64))
 status:Mapped[str]=mapped_column(String(30),default="valid")
 invalidated_at:Mapped[str]=mapped_column(String(64),default="")
 invalidated_by:Mapped[str]=mapped_column(String(160),default="")
 invalidated_reason:Mapped[str]=mapped_column(Text,default="")
 invalidated_review_id:Mapped[str]=mapped_column(String(80),default="")
 accepted_note:Mapped[str]=mapped_column(Text,default="")
 accepted_author:Mapped[str]=mapped_column(String(160),default="")
 result_checksum:Mapped[str]=mapped_column(String(80),default="")
 snapshot:Mapped[dict]=mapped_column(JSON,default=dict)
