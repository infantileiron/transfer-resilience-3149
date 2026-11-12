from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class TransferArc(Base):
 __tablename__="transfer_arcs"
 __table_args__=(UniqueConstraint("dataset_id","arc_id"),)
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey("network_datasets.id"))
 arc_id:Mapped[str]=mapped_column(String(60))
 source:Mapped[str]=mapped_column(String(60))
 target:Mapped[str]=mapped_column(String(60))
 capacity:Mapped[int]=mapped_column(Integer)
 travel_minutes:Mapped[float]=mapped_column(Double)
 created_at:Mapped[str]=mapped_column(String(64))
