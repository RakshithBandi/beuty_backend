from pydantic import BaseModel
from typing import Optional, List

# Services
class ServiceBase(BaseModel):
    name: str
    category: str
    price: Optional[str] = None
    duration: Optional[str] = None
    staff: Optional[str] = None
    img: Optional[str] = None
    description: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: int
    class Config:
        from_attributes = True

# Bookings
class BookingBase(BaseModel):
    service_id: int
    client: str
    date: str
    price: Optional[str] = None
    status: Optional[str] = "Confirmed"

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    service_name: Optional[str] = None
    class Config:
        from_attributes = True

# Customers
class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    last_visit: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    class Config:
        from_attributes = True

# Auth
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    role: str
    class Config:
        from_attributes = True
