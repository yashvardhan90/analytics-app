from fastapi import FastAPI, HTTPException, Depends, Request, Header
from typing import Annotated, List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import httpagentparser, hashlib
from datetime import datetime
# from pydantic import BaseModel

app = FastAPI()

@app.get('/')
async def check():
    return 'hello'

origins = [
    "https://yasharma.xyz",
    "http://localhost:1313/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class VisitBase(BaseModel):
    ip_hash: str
    ip_address: str
    device: Optional[str] = None
    browser: Optional[str] = None
    date: str
    url: str

class VisitModel(VisitBase):
    id: int
    # class Config:
    #     orm_mode = True

class VisitLocked(BaseModel):
    url: str

class VisitLockedModel(VisitLocked):
    id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
models.Base.metadata.create_all(bind=engine)

@app.get("/track/", response_model=VisitLockedModel)
async def track(url: str, db:db_dependency, request: Request, user_agent: Annotated[str | None, Header()] = None):
    # Extract data from the request
    ip_address = request.client.host
    port = request.client.port

    agent = httpagentparser.detect(user_agent)
    device = agent.get('platform', {}).get('name', '')
    browser = agent.get('browser', {}).get('name', '')

   # Extract data from the request
    ip_address = request.client.host
    port = request.client.port

    agent = httpagentparser.detect(user_agent)
    device = agent.get('platform', {}).get('name', '')
    browser = agent.get('browser', {}).get('name', '')

    # Generate ip_hash
    hash = ip_hash(ip_address)

    # Create a new Visit instance with generated and extracted data
    visit_data = {
        "ip_hash": hash,
        "ip_address": ip_address,
        "device": device,
        "browser": browser,
        "date": datetime.utcnow(),
        "url": url
    }

    print("Device:", device)

    db_visit = models.Visit(**visit_data)
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit


@app.get("/getdata/", response_model=List[VisitModel])
async def getdata(db: db_dependency, skip: int=0, limit: int=100):
    visits = db.query(models.Visit).offset(skip).limit(limit).all()
    return visits

def ip_hash(ip_address):
        ip = ip_address + "-" + str(datetime.utcnow())
        return hashlib.md5(ip.encode()).hexdigest()











