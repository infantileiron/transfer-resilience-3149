from sqlalchemy import String,Double,Integer,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class User(Base):
 __tablename__="users"
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 email:Mapped[str]=mapped_column(String(160),unique=True)
 password:Mapped[str]=mapped_column(String(255))
 role:Mapped[str]=mapped_column(String(30))
