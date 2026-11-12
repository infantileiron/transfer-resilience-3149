from pydantic import BaseModel,Field,model_validator
from src.schemas.arc import ArcDefinition
class Node(BaseModel):
 node_id:str=Field(min_length=1,max_length=60)
 label:str=Field(min_length=1,max_length=80)
 x:float|None=Field(default=None,ge=0,le=100,allow_inf_nan=False)
 y:float|None=Field(default=None,ge=0,le=100,allow_inf_nan=False)
class DatasetInput(BaseModel):
 name:str=Field(min_length=2,max_length=120)
 source:str=Field(default="transfer_network.json",max_length=120)
 nodes:list[Node]=Field(min_length=2,max_length=30)
 arcs:list[ArcDefinition]=Field(default_factory=list,max_length=200)
 @model_validator(mode="after")
 def valid(self):
  nodes={n.node_id for n in self.nodes}
  if len(nodes)!=len(self.nodes):raise ValueError("节点ID不能重复")
  if len({a.arc_id for a in self.arcs})!=len(self.arcs):raise ValueError("边ID不能重复；平行和反向边须各用独立ID")
  if any(a.source not in nodes or a.target not in nodes for a in self.arcs):raise ValueError("边端点必须在节点集合中")
  return self
