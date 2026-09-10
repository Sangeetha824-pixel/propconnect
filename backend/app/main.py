import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, or_
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./propconnect.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
SECRET = os.getenv('JWT_SECRET', 'propconnect-demo-secret')
pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2 = OAuth2PasswordBearer(tokenUrl='/api/auth/login')

class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'; id: Mapped[int]=mapped_column(primary_key=True); name: Mapped[str]=mapped_column(String(120)); email: Mapped[str]=mapped_column(String(180), unique=True); password_hash: Mapped[str]=mapped_column(String(255)); role: Mapped[str]=mapped_column(String(20), default='buyer'); preferred_location: Mapped[Optional[str]]=mapped_column(String(120), nullable=True); preferred_budget: Mapped[Optional[float]]=mapped_column(Float, nullable=True); preferred_type: Mapped[Optional[str]]=mapped_column(String(40), nullable=True)
class Property(Base):
    __tablename__='properties'; id: Mapped[int]=mapped_column(primary_key=True); seller_id: Mapped[int]=mapped_column(ForeignKey('users.id')); title: Mapped[str]=mapped_column(String(180)); description: Mapped[str]=mapped_column(Text); location: Mapped[str]=mapped_column(String(180)); property_type: Mapped[str]=mapped_column(String(50)); rooms: Mapped[int]=mapped_column(Integer); price: Mapped[float]=mapped_column(Float); images: Mapped[str]=mapped_column(Text, default=''); active: Mapped[bool]=mapped_column(Boolean, default=True); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Favourite(Base):
    __tablename__='favourites'; id: Mapped[int]=mapped_column(primary_key=True); buyer_id: Mapped[int]=mapped_column(ForeignKey('users.id')); property_id: Mapped[int]=mapped_column(ForeignKey('properties.id')); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Interest(Base):
    __tablename__='interests'; id: Mapped[int]=mapped_column(primary_key=True); buyer_id: Mapped[int]=mapped_column(ForeignKey('users.id')); property_id: Mapped[int]=mapped_column(ForeignKey('properties.id')); status: Mapped[str]=mapped_column(String(20), default='New'); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class SearchHistory(Base):
    __tablename__='search_history'; id: Mapped[int]=mapped_column(primary_key=True); buyer_id: Mapped[int]=mapped_column(ForeignKey('users.id')); query: Mapped[str]=mapped_column(String(180)); property_type: Mapped[Optional[str]]=mapped_column(String(50), nullable=True); min_budget: Mapped[Optional[float]]=mapped_column(Float, nullable=True); max_budget: Mapped[Optional[float]]=mapped_column(Float, nullable=True); created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
Base.metadata.create_all(engine)
app=FastAPI(title='PropConnect API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv('FRONTEND_ORIGIN','http://localhost:5173')], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
@app.get('/')
def health():
    return {'service': 'PropConnect API', 'status': 'ok', 'docs': '/docs'}
class Register(BaseModel): name: str; email: EmailStr; password: str; role: str='buyer'
class Login(BaseModel): email: EmailStr; password: str
class PropertyIn(BaseModel): title: str; description: str=''; location: str; property_type: str; rooms: int; price: float; images: list[str]=[]; active: bool=True
def token_for(user): return jwt.encode({'sub':str(user.id),'role':user.role,'exp':datetime.utcnow()+timedelta(hours=12)}, SECRET, algorithm='HS256')
def current_user(token: str=Depends(oauth2), db: Session=Depends(lambda: SessionLocal())):
    try: uid=jwt.decode(token, SECRET, algorithms=['HS256'])['sub']
    except (JWTError, KeyError): raise HTTPException(401,'Invalid authentication credentials')
    user=db.get(User,int(uid)); db.close()
    if not user: raise HTTPException(401,'User not found')
    return user
def public_user(u): return {'id':u.id,'name':u.name,'email':u.email,'role':u.role}
def public_property(p): return {'id':p.id,'title':p.title,'description':p.description,'location':p.location,'type':p.property_type,'rooms':p.rooms,'price':p.price,'images':p.images.split(',') if p.images else [],'active':p.active,'seller_id':p.seller_id}
@app.post('/api/auth/register')
def register(data:Register):
    db=SessionLocal()
    if db.query(User).filter_by(email=data.email).first(): raise HTTPException(400,'Email already registered')
    u=User(name=data.name,email=data.email,password_hash=pwd.hash(data.password),role=data.role); db.add(u); db.commit(); db.refresh(u); out={'access_token':token_for(u),'token_type':'bearer','user':public_user(u)}; db.close(); return out
@app.post('/api/auth/login')
def login(data:Login):
    db=SessionLocal(); u=db.query(User).filter_by(email=data.email).first()
    if not u or not pwd.verify(data.password,u.password_hash): raise HTTPException(401,'Incorrect email or password')
    out={'access_token':token_for(u),'token_type':'bearer','user':public_user(u)}; db.close(); return out
@app.get('/api/properties')
def properties(location:str='', min_budget:float=0, max_budget:float=0, property_type:str='', sort:str='', user=Depends(current_user)):
    db=SessionLocal(); q=db.query(Property).filter(Property.active.is_(True))
    if location: q=q.filter(Property.location.ilike(f'%{location}%'))
    if min_budget: q=q.filter(Property.price>=min_budget)
    if max_budget: q=q.filter(Property.price<=max_budget)
    if property_type: q=q.filter(Property.property_type==property_type)
    if sort=='asc': q=q.order_by(Property.price.asc())
    if sort=='desc': q=q.order_by(Property.price.desc())
    if location or property_type: db.add(SearchHistory(buyer_id=user.id,query=location,property_type=property_type,min_budget=min_budget,max_budget=max_budget)); db.commit()
    out=[public_property(p) for p in q.all()]; db.close(); return out
@app.get('/api/properties/{pid}')
def property_detail(pid:int,user=Depends(current_user)):
    db=SessionLocal(); p=db.get(Property,pid); db.close()
    if not p: raise HTTPException(404,'Property not found')
    return public_property(p)
@app.post('/api/properties')
def create_property(data:PropertyIn,user=Depends(current_user)):
    if user.role!='seller': raise HTTPException(403,'Seller access required')
    db=SessionLocal(); p=Property(seller_id=user.id,images=','.join(data.images),**data.model_dump(exclude={'images'})); db.add(p); db.commit(); db.refresh(p); out=public_property(p); db.close(); return out
@app.put('/api/properties/{pid}')
def update_property(pid:int,data:PropertyIn,user=Depends(current_user)):
    db=SessionLocal(); p=db.get(Property,pid)
    if not p or p.seller_id!=user.id: raise HTTPException(404,'Listing not found')
    for k,v in data.model_dump(exclude={'images'}).items(): setattr(p,k,v)
    p.images=','.join(data.images); db.commit(); out=public_property(p); db.close(); return out
@app.delete('/api/properties/{pid}')
def delete_property(pid:int,user=Depends(current_user)):
    db=SessionLocal(); p=db.get(Property,pid)
    if not p or p.seller_id!=user.id: raise HTTPException(404,'Listing not found')
    db.delete(p); db.commit(); db.close(); return {'ok':True}
@app.post('/api/properties/{pid}/favorite')
def favorite(pid:int,user=Depends(current_user)):
    db=SessionLocal(); found=db.query(Favourite).filter_by(buyer_id=user.id,property_id=pid).first()
    if found: db.delete(found); saved=False
    else: db.add(Favourite(buyer_id=user.id,property_id=pid)); saved=True
    db.commit(); db.close(); return {'saved':saved}
@app.post('/api/properties/{pid}/interest')
def interest(pid:int,user=Depends(current_user)):
    db=SessionLocal(); found=db.query(Interest).filter_by(buyer_id=user.id,property_id=pid).first()
    if found: return {'status':found.status}
    db.add(Interest(buyer_id=user.id,property_id=pid)); db.commit(); db.close(); return {'status':'New'}
@app.get('/api/seller/interests')
def seller_interests(user=Depends(current_user)):
    db=SessionLocal(); rows=db.query(Interest,Property,User).join(Property,Interest.property_id==Property.id).join(User,Interest.buyer_id==User.id).filter(Property.seller_id==user.id).all(); out=[{'id':i.id,'property':p.title,'buyer':public_user(b),'status':i.status,'created_at':i.created_at} for i,p,b in rows]; db.close(); return out
@app.get('/api/recommendations')
def recommendations(user=Depends(current_user)):
    db=SessionLocal(); fav_types=[p.property_type for f in db.query(Favourite).filter_by(buyer_id=user.id).all() for p in [db.get(Property,f.property_id)]]; history=db.query(SearchHistory).filter_by(buyer_id=user.id).order_by(SearchHistory.created_at.desc()).first(); q=db.query(Property).filter(Property.active.is_(True)); candidates=q.all(); ranked=sorted(candidates,key=lambda p:(2 if p.property_type in fav_types else 0)+(1 if history and history.query.lower() in p.location.lower() else 0)+(1 if user.preferred_location and user.preferred_location.lower() in p.location.lower() else 0),reverse=True); out=[public_property(p) for p in ranked[:8]]; db.close(); return out
