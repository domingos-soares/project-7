import uuid
from sqlalchemy import Boolean, Column, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class ItemModel(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)
