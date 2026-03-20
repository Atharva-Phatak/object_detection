from pydantic import BaseModel
from typing import List


class Box(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float


class Prediction(BaseModel):
    class_name: str
    score: float
    box: Box


class ObjectCount(BaseModel):
    object_class: str
    count: int


class CountResponse(BaseModel):
    current_objects: List[ObjectCount]
    total_objects: List[ObjectCount]
