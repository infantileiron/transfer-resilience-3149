from pydantic import BaseModel,Field
class ArcDefinition(BaseModel):
 arc_id:str=Field(min_length=1,max_length=60)
 source:str=Field(min_length=1,max_length=60)
 target:str=Field(min_length=1,max_length=60)
 capacity:int=Field(ge=0,le=1000000,strict=True)
 travel_minutes:float=Field(ge=0,le=1000000,allow_inf_nan=False)
class ArcInput(ArcDefinition):dataset_id:str
