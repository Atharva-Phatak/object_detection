from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class BoxRecord(Base):
    __tablename__ = "boxes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    xmin = Column(Float, nullable=False)
    ymin = Column(Float, nullable=False)
    xmax = Column(Float, nullable=False)
    ymax = Column(Float, nullable=False)
    prediction = relationship("PredictionRecord", back_populates="box", uselist=False)


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(String(128), nullable=False)
    score = Column(Float, nullable=False)
    box_id = Column(Integer, ForeignKey("boxes.id"), nullable=False)
    box = relationship("BoxRecord", back_populates="prediction")


class ObjectCountRecord(Base):
    __tablename__ = "object_counts"

    object_class = Column(String(128), primary_key=True, nullable=False)
    count = Column(Integer, nullable=False, default=0)
