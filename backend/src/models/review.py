from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ResilienceReview(Base):
 __tablename__="resilience_reviews"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("network_runs.id"))
 note:Mapped[str]=mapped_column(Text)
 decision:Mapped[str]=mapped_column(String(30))
 author:Mapped[str]=mapped_column(String(160))
 created_at:Mapped[str]=mapped_column(String(64))
