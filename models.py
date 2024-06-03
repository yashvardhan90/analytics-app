from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float

class Visit(Base):
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True, index=True)
    ip_hash = Column(String)
    ip_address = Column(String)
    device = Column(String)
    browser = Column(String)
    date = Column(String)
    url = Column(String)

