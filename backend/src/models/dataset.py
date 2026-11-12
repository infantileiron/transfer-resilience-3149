from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class NetworkDataset(Base):
 __tablename__="network_datasets"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 name:Mapped[str]=mapped_column(String(160),unique=True)
 source:Mapped[str]=mapped_column(String(160))
 nodes:Mapped[list]=mapped_column(JSON)
 created_at:Mapped[str]=mapped_column(String(64))
