from pydantic import BaseModel
from typing import Optional, List
from datetime import time

class CustomerCreate(BaseModel):
    Name: str
    Email: str
    Password: str
    Mobile_No: str
    Address: str
    City: str
    Pincode: str

class CustomerResponse(BaseModel):
    C_ID: int
    Name: str
    Email: str

    class Config:
        from_attributes = True

class DeliveryPersonCreate(BaseModel):
    Name: str
    Email: str
    Password: str
    Phone_Number: str

class DeliveryPersonResponse(BaseModel):
    D_ID: int
    Name: str
    Email: str
    Phone_Number: str
    Availability: bool

    class Config:
        from_attributes = True

class DeliveryOrderResponse(BaseModel):
    O_ID: int
    Customer_Name: str
    Customer_Phone: str
    Delivery_Address: str
    Total_Amount: float
    Order_Status: str

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str # "customer", "restaurant", or "admin"

class Token(BaseModel):
    access_token: str
    token_type: str

class RestaurantCreate(BaseModel):
    Name: str
    Email: str
    Password: str
    Location: str
    Phone_Number: str
    Rating: Optional[float] = 0.0

class RestaurantResponse(BaseModel):
    R_ID: int
    Name: str
    Location: str
    Rating: Optional[float] = None
    discount_percentage: float
    discount_start_time: Optional[time] = None
    discount_end_time: Optional[time] = None
    is_discount_active: bool
    class Config:
        from_attributes = True

class RestaurantDiscountUpdate(BaseModel):
    percentage: float
    start_time: time
    end_time: time
    is_active: bool

class FoodItemCreate(BaseModel):
    R_ID: int
    Food_Name: str
    Category: str
    Price: float
    Availability: bool = True

class FoodItemResponse(BaseModel):
    Food_ID: int
    R_ID: int
    Food_Name: str
    Category: str
    Price: float
    Availability: bool
    class Config:
        from_attributes = True

class CartItemAdd(BaseModel):
    Food_ID: int
    Quantity: int = 1

class CartItemResponse(BaseModel):
    Food_ID: int
    Food_Name: str
    Price: float
    Quantity: int
    Subtotal: float
    R_ID: int
    Restaurant_Name: str

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    Total_Amount: float
    Discount_Amount: float = 0.0
    Final_Amount: float
    Night_Offer_Applied: bool = False

class OrderResponse(BaseModel):
    O_ID: int
    Total_Amount: float
    Discount_Amount: float
    Final_Amount: float
    Order_Status: str
    class Config:
        from_attributes = True

class OrderHistoryResponse(BaseModel):
    O_ID: int
    Restaurant_Name: str
    Final_Amount: float
    Order_Status: str
    Date: str
    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    Payment_Mode: str

class CheckoutRequest(BaseModel):
    Payment_Mode: str

class OrderStatusUpdate(BaseModel):
    Order_Status: str

class RestaurantAnalyticsResponse(BaseModel):
    Total_Orders: int
    Total_Revenue: float

class AdminReportResponse(BaseModel):
    Total_Users: int
    Total_Restaurants: int
    Total_Delivery_Personnel: int
    Total_Orders: int
    Total_Revenue: float

from datetime import time

class DiscountCreate(BaseModel):
    percentage: float
    start_time: time
    end_time: time
    is_active: bool = True

class DiscountResponse(BaseModel):
    id: int
    percentage: float
    start_time: time
    end_time: time
    is_active: bool
    class Config:
        from_attributes = True