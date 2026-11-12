from pydantic import BaseModel,Field,model_validator
class ScenarioInput(BaseModel):
 name:str=Field(min_length=2,max_length=120)
 dataset_id:str
 source_node:str
 sink_node:str
 disabled_arc_ids:list[str]=Field(default_factory=list,max_length=200)
 @model_validator(mode="after")
 def valid(self):
  if self.source_node==self.sink_node:raise ValueError("源汇必须不同")
  if len(set(self.disabled_arc_ids))!=len(self.disabled_arc_ids):raise ValueError("停用边ID不能重复")
  return self
