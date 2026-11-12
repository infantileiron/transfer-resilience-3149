from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class OutageScenario(Base):
 __tablename__="outage_scenarios"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 name:Mapped[str]=mapped_column(String(160),unique=True)
 dataset_id:Mapped[str]=mapped_column(ForeignKey("network_datasets.id"))
 source_node:Mapped[str]=mapped_column(String(60))
 sink_node:Mapped[str]=mapped_column(String(60))
 disabled_arc_ids:Mapped[list]=mapped_column(JSON)
 arc_snapshot:Mapped[list]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String(64))
