from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from contextlib import asynccontextmanager
import models, schemas, database
from database import engine, get_db
from passlib.context import CryptContext

# Create tables
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed database
    db = next(get_db())
    try:
        seed_db(db)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error during database seeding: {e}")
    yield
    # Shutdown logic (if any) can go here

app = FastAPI(title="Beauty Parlour API", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed data
def seed_db(db: Session):
    # Seed Services
    if db.query(models.Service).count() == 0:
        services = [
            # Hair Care
            models.Service(name='Hair Styling & Cutting', category='HAIR CARE', price='$85.00', duration='60 min', staff='Samantha W.', img='https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&q=80&w=400', description='Expert hair cutting and styling tailored to your face shape.'),
            models.Service(name='Hair Coloring', category='HAIR CARE', price='$120.00', duration='120 min', staff='Samantha W.', img='https://images.unsplash.com/photo-1560869713-7d0a29430863?auto=format&fit=crop&q=80&w=400', description='Full head coloring or highlights using premium ammonia-free products.'),
            
            # Skin Care
            models.Service(name='Luxury Spa Facial', category='SKIN CARE', price='$120.00', duration='90 min', staff='Jessica K.', img='https://images.unsplash.com/photo-1512290923902-8a9f81dc236c?auto=format&fit=crop&q=80&w=400', description='Rejuvenating facial treatment using premium organic products.'),
            models.Service(name='Deep Cleansing', category='SKIN CARE', price='$65.00', duration='45 min', staff='Jessica K.', img='https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&q=80&w=400', description='Professional pore cleaning and skin detoxification.'),
            
            # Makeup
            models.Service(name='Bridal Makeup', category='MAKEUP', price='$350.00', duration='240 min', staff='Lisa T.', img='https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&q=80&w=400', description='Complete bridal look including hair and makeup.'),
            models.Service(name='Party Makeup', category='MAKEUP', price='$150.00', duration='90 min', staff='Lisa T.', img='https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&q=80&w=400', description='Elegant makeup for parties and special occasions.'),
            
            # Nails (Manicure/Pedicure)
            models.Service(name='Premium Manicure', category='SERVICES', price='$45.00', duration='45 min', staff='Lisa T.', img='https://images.unsplash.com/photo-1519014816548-bf5fe059798b?auto=format&fit=crop&q=80&w=400', description='Complete nail care including shaping and polish.'),
            
            # Salon at Home
            models.Service(name='Home Spa Ritual', category='SALON AT HOME', price='$180.00', duration='120 min', staff='Staff A', img='https://images.unsplash.com/photo-1544161515-4af6b1d462c2?auto=format&fit=crop&q=80&w=400', description='Full spa experience delivered to your doorstep.')
        ]
        db.add_all(services)
        db.commit()
    
    # Seed Default Admin
    if db.query(models.User).filter(models.User.role == "admin").count() == 0:
        admin = models.User(
            username="admin",
            email="admin@beautyflow.com",
            hashed_password=get_password_hash("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

# Removed deprecated startup_event

# Auth API
@app.post("/api/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check username
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check email
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role="user" # Default to user
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Look for user by username OR email
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.username)
    ).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role
    }

# Services API
@app.get("/api/services", response_model=List[schemas.Service])
def get_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()

@app.post("/api/services", response_model=schemas.Service)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db_service = models.Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@app.put("/api/services/{service_id}")
def update_service(service_id: int, service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    for key, value in service.model_dump().items():
        setattr(db_service, key, value)
    
    db.commit()
    return {"success": True}

@app.delete("/api/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    db_service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(db_service)
    db.commit()
    return {"success": True}

# Bookings API
@app.get("/api/bookings", response_model=List[schemas.Booking])
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).all()
    result = []
    for b in bookings:
        # Create a dictionary from the booking object
        booking_data = {
            "id": b.id,
            "service_id": b.service_id,
            "client": b.client,
            "date": b.date,
            "price": b.price,
            "status": b.status,
            "service_name": b.service.name if b.service else "Unknown"
        }
        result.append(booking_data)
    return result

@app.post("/api/bookings", response_model=schemas.Booking)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    db_booking = models.Booking(**booking.model_dump())
    db.add(db_booking)
    
    # Track customer
    customer = db.query(models.Customer).filter(models.Customer.name == booking.client).first()
    if not customer:
        new_customer = models.Customer(name=booking.client, last_visit=booking.date)
        db.add(new_customer)
    else:
        customer.last_visit = booking.date
    
    db.commit()
    db.refresh(db_booking)
    
    # Return as dict with service_name
    return {
        "id": db_booking.id,
        "service_id": db_booking.service_id,
        "client": db_booking.client,
        "date": db_booking.date,
        "price": db_booking.price,
        "status": db_booking.status,
        "service_name": db_booking.service_name
    }

# Customers API
@app.get("/api/customers", response_model=List[schemas.Customer])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
