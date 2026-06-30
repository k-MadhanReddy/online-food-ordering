from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

import database
import models
import schemas
import auth

router = APIRouter(prefix="/api/admin", tags=["Admin Features"])

# --- User Management ---

@router.get("/users", response_model=list[schemas.CustomerResponse])
def get_all_users(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    return db.query(models.Customer).all()

@router.delete("/users/{c_id}")
def delete_user(c_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    user = db.query(models.Customer).filter(models.Customer.C_ID == c_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(user)
    db.commit()
    return {"message": "Customer deleted successfully"}

@router.post("/customers", response_model=schemas.CustomerResponse)
def admin_create_customer(customer: schemas.CustomerCreate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    db_cust = db.query(models.Customer).filter(models.Customer.Email == customer.Email).first()
    if db_cust:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = auth.get_password_hash(customer.Password)
    new_customer = models.Customer(
        Name=customer.Name,
        Email=customer.Email,
        Password=hashed_password,
        Mobile_No=customer.Mobile_No,
        Address=customer.Address,
        City=customer.City,
        Pincode=customer.Pincode
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

# --- Restaurant Management ---

@router.get("/restaurants", response_model=list[schemas.RestaurantResponse])
def get_all_restaurants(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    return db.query(models.Restaurant).all()

@router.post("/restaurants", response_model=schemas.RestaurantResponse)
def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    db_rest = db.query(models.Restaurant).filter(models.Restaurant.Email == restaurant.Email).first()
    if db_rest:
        raise HTTPException(status_code=400, detail="Restaurant email already registered")
        
    hashed_password = auth.get_password_hash(restaurant.Password)
    new_restaurant = models.Restaurant(
        Name=restaurant.Name,
        Email=restaurant.Email,
        Password=hashed_password,
        Location=restaurant.Location,
        Phone_Number=restaurant.Phone_Number,
        Rating=restaurant.Rating
    )
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)
    return new_restaurant

@router.delete("/restaurants/{r_id}")
def delete_restaurant(r_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.R_ID == r_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    db.delete(restaurant)
    db.commit()
    return {"message": "Restaurant deleted successfully"}

# --- Menu Item Management ---

@router.get("/menu", response_model=list[schemas.FoodItemResponse])
def get_all_menu_items(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    return db.query(models.FoodItem).all()

@router.post("/menu", response_model=schemas.FoodItemResponse)
def create_menu_item(item: schemas.FoodItemCreate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    # Verify restaurant exists
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.R_ID == item.R_ID).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
        
    new_item = models.FoodItem(
        R_ID=item.R_ID,
        Food_Name=item.Food_Name,
        Category=item.Category,
        Price=item.Price,
        Availability=item.Availability
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.delete("/menu/{food_id}")
def delete_menu_item(food_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    item = db.query(models.FoodItem).filter(models.FoodItem.Food_ID == food_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    db.delete(item)
    db.commit()
    return {"message": "Food item deleted successfully"}

# --- Order Management ---

@router.get("/orders")
def get_all_orders_for_admin(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    # Join with Restaurant and DeliveryPerson to get names
    # Filter for ONLY active orders (not Delivered/Cancelled)
    orders = db.query(models.Order, models.Restaurant, models.DeliveryPerson)\
        .join(models.Restaurant, models.Order.R_ID == models.Restaurant.R_ID)\
        .outerjoin(models.DeliveryPerson, models.Order.D_ID == models.DeliveryPerson.D_ID)\
        .filter(models.Order.Order_Status.notin_(["Delivered", "Cancelled"]))\
        .all()
    
    res = []
    for order, restaurant, delivery in orders:
        res.append({
            "O_ID": order.O_ID,
            "Restaurant_Name": restaurant.Name,
            "Order_Status": order.Order_Status,
            "Delivery_Name": delivery.Name if delivery else "Not Assigned",
            "D_ID": order.D_ID
        })
    return res

# --- Delivery Personnel Management ---

@router.get("/delivery", response_model=list[schemas.DeliveryPersonResponse])
def get_all_delivery_persons(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    return db.query(models.DeliveryPerson).all()

@router.post("/delivery", response_model=schemas.DeliveryPersonResponse)
def create_delivery_person(dp: schemas.DeliveryPersonCreate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    db_dp = db.query(models.DeliveryPerson).filter(models.DeliveryPerson.Email == dp.Email).first()
    if db_dp:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = auth.get_password_hash(dp.Password)
    new_dp = models.DeliveryPerson(
        Name=dp.Name,
        Email=dp.Email,
        Password=hashed_password,
        Phone_Number=dp.Phone_Number,
        Availability=True
    )
    db.add(new_dp)
    db.commit()
    db.refresh(new_dp)
    return new_dp

@router.delete("/delivery/{d_id}")
def delete_delivery_person(d_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    dp = db.query(models.DeliveryPerson).filter(models.DeliveryPerson.D_ID == d_id).first()
    if not dp:
        raise HTTPException(status_code=404, detail="Delivery personnel not found")
    db.delete(dp)
    db.commit()
    return {"message": "Delivery personnel deleted successfully"}

@router.put("/order/{o_id}/assign/{d_id}")
def assign_delivery_to_order(o_id: int, d_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    order = db.query(models.Order).filter(models.Order.O_ID == o_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.Order_Status in ["Delivered", "Cancelled"]:
        raise HTTPException(status_code=400, detail="Cannot assign delivery for completed or cancelled order")
        
    if order.D_ID:
        raise HTTPException(status_code=400, detail="Order is already assigned to a delivery personnel")
        
    dp = db.query(models.DeliveryPerson).filter(models.DeliveryPerson.D_ID == d_id).first()
    if not dp:
        raise HTTPException(status_code=404, detail="Delivery personnel not found")
        
    order.D_ID = d_id
    db.commit()
    return {"message": f"Order #{o_id} assigned to {dp.Name}"}

# --- Reports ---

@router.get("/reports", response_model=schemas.AdminReportResponse)
def view_reports(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
    try:
        total_users = db.query(models.Customer).count()
        total_restaurants = db.query(models.Restaurant).count()
        total_delivery = db.query(models.DeliveryPerson).count()
        total_orders = db.query(models.Order).count()
        
        # Calculate total revenue from successful payments
        revenue_result = db.query(func.sum(models.Payment.Amount)).filter(models.Payment.Payment_Status == "Success").scalar()
        total_revenue = float(revenue_result) if revenue_result else 0.0
        
        return schemas.AdminReportResponse(
            Total_Users=total_users,
            Total_Restaurants=total_restaurants,
            Total_Delivery_Personnel=total_delivery,
            Total_Orders=total_orders,
            Total_Revenue=total_revenue
        )
    except Exception as e:
        print(f"Error in reports: {e}")
        return schemas.AdminReportResponse(
            Total_Users=0, Total_Restaurants=0, Total_Delivery_Personnel=0, Total_Orders=0, Total_Revenue=0.0
        )

# --- Discount Management ---

# @router.post("/discount", response_model=schemas.DiscountResponse)
# def set_night_discount(discount: schemas.DiscountCreate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["admin"]))):
#     # Deactivate all current discounts
#     db.query(models.Discount).update({models.Discount.is_active: False})
#     
#     # Create new discount
#     new_discount = models.Discount(
#         percentage=discount.percentage,
#         start_time=discount.start_time,
#         end_time=discount.end_time,
#         is_active=discount.is_active
#     )
#     db.add(new_discount)
#     db.commit()
#     db.refresh(new_discount)
#     return new_discount
