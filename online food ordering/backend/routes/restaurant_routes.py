from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

import database
import models
import schemas
import auth

router = APIRouter(prefix="/api/restaurant", tags=["Restaurant Features"])

@router.get("/orders", response_model=list[schemas.OrderResponse])
def view_incoming_orders(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["restaurant"]))):
    # Retrieve all orders belonging to the authenticated restaurant
    orders = db.query(models.Order).filter(models.Order.R_ID == current_user.R_ID).all()
    return orders

@router.post("/orders/{o_id}/status", response_model=schemas.OrderResponse)
def update_order_status(o_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["restaurant"]))):
    # Verify the order belongs to this restaurant
    order = db.query(models.Order).filter(models.Order.O_ID == o_id, models.Order.R_ID == current_user.R_ID).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or access denied")
        
    valid_statuses = ["Accepted", "Rejected", "Preparing", "Ready", "Out for delivery", "Delivered"]
    
    if status_update.Order_Status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
    order.Order_Status = status_update.Order_Status
    db.commit()
    db.refresh(order)
    
    return order

@router.get("/profile", response_model=schemas.RestaurantResponse)
def get_profile(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["restaurant"]))):
    return db.query(models.Restaurant).filter(models.Restaurant.R_ID == current_user.R_ID).first()

@router.post("/discount", response_model=schemas.RestaurantResponse)
def update_discount(discount: schemas.RestaurantDiscountUpdate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["restaurant"]))):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.R_ID == current_user.R_ID).first()
    
    restaurant.discount_percentage = discount.percentage
    restaurant.discount_start_time = discount.start_time
    restaurant.discount_end_time = discount.end_time
    restaurant.is_discount_active = discount.is_active
    
    db.commit()
    db.refresh(restaurant)
    return restaurant

@router.get("/analytics", response_model=schemas.RestaurantAnalyticsResponse)
def get_restaurant_analytics(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["restaurant"]))):
    r_id = current_user.R_ID
    
    total_orders = db.query(models.Order).filter(models.Order.R_ID == r_id).count()
    
    # Sum revenue from successful payments for this restaurant's orders
    revenue_result = db.query(func.sum(models.Payment.Amount)).join(models.Order).filter(models.Order.R_ID == r_id, models.Payment.Payment_Status == "Success").scalar()
    total_revenue = revenue_result if revenue_result else 0.0
    
    return schemas.RestaurantAnalyticsResponse(
        Total_Orders=total_orders,
        Total_Revenue=total_revenue
    )

@router.get("/menu", response_model=list[schemas.FoodItemResponse])
def get_my_menu(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["restaurant"]))):
    return db.query(models.FoodItem).filter(models.FoodItem.R_ID == current_user.R_ID).all()

@router.post("/menu", response_model=schemas.FoodItemResponse)
def add_menu_item(item: schemas.FoodItemCreate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["restaurant"]))):
    # Ensure the R_ID in the request matches the logged-in restaurant
    if item.R_ID != current_user.R_ID:
        raise HTTPException(status_code=403, detail="Cannot add menu items for other restaurants")
        
    new_item = models.FoodItem(
        R_ID=current_user.R_ID,
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
def remove_menu_item(food_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["restaurant"]))):
    item = db.query(models.FoodItem).filter(models.FoodItem.Food_ID == food_id, models.FoodItem.R_ID == current_user.R_ID).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found in your restaurant")
    db.delete(item)
    db.commit()
    return {"message": "Menu item removed"}
