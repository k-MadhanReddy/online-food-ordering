from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    C_ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Email = Column(String, unique=True, index=True)
    Password = Column(String)
    Mobile_No = Column(String)
    Address = Column(String)
    City = Column(String)
    Pincode = Column(String)

    # Relationship to orders with cascade delete
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    R_ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Email = Column(String, unique=True, index=True)
    Password = Column(String)
    Location = Column(String)
    Phone_Number = Column(String)
    Rating = Column(Float)
    
    # Restaurant-controlled discount
    discount_percentage = Column(Float, default=0.0)
    discount_start_time = Column(Time, nullable=True)
    discount_end_time = Column(Time, nullable=True)
    is_discount_active = Column(Boolean, default=False)

    food_items = relationship("FoodItem", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")

class FoodItem(Base):
    __tablename__ = "food_items"
    
    Food_ID = Column(Integer, primary_key=True, index=True)
    R_ID = Column(Integer, ForeignKey("restaurants.R_ID"))
    Food_Name = Column(String, index=True)
    Category = Column(String)
    Price = Column(Float)
    Availability = Column(Boolean, default=True)

    restaurant = relationship("Restaurant", back_populates="food_items")

class Order(Base):
    __tablename__ = "orders"
    
    O_ID = Column(Integer, primary_key=True, index=True)
    C_ID = Column(Integer, ForeignKey("customers.C_ID"))
    R_ID = Column(Integer, ForeignKey("restaurants.R_ID"))
    Total_Amount = Column(Float)
    Discount_Amount = Column(Float, default=0.0)
    Final_Amount = Column(Float)
    Order_Status = Column(String, default="Pending")
    Date = Column(Date)
    Time = Column(Time)

    customer = relationship("Customer", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    payment = relationship("Payment", back_populates="order", uselist=False)
    
    D_ID = Column(Integer, ForeignKey("delivery_persons.D_ID"), nullable=True)
    delivery_person = relationship("DeliveryPerson", back_populates="orders")

class Payment(Base):
    __tablename__ = "payments"
    
    Payment_ID = Column(Integer, primary_key=True, index=True)
    O_ID = Column(Integer, ForeignKey("orders.O_ID"), unique=True)
    Amount = Column(Float)
    Payment_Mode = Column(String)
    Payment_Status = Column(String, default="Pending")
    Date = Column(Date)

    order = relationship("Order", back_populates="payment")

class Admin(Base):
    __tablename__ = "admins"
    
    A_ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Email = Column(String, unique=True, index=True)
    Password = Column(String)

class DeliveryPerson(Base):
    __tablename__ = "delivery_persons"
    
    D_ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Email = Column(String, unique=True, index=True)
    Password = Column(String)
    Phone_Number = Column(String)
    Availability = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="delivery_person")

class Discount(Base):
    __tablename__ = "discounts"
    
    id = Column(Integer, primary_key=True, index=True)
    percentage = Column(Float)
    start_time = Column(Time)
    end_time = Column(Time)
    is_active = Column(Boolean, default=True)
