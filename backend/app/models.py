from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Standard(Base):
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, index=True)
    is_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="Active")
    source_url = Column(String(500), nullable=True)