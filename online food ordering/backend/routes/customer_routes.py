from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, datetime

import database
import models
import schemas
import auth

router = APIRouter(prefix="/api/customer", tags=["Customer Features"])

# --- Helper: Calculate Night Discount ---
def calculate_discount(db: Session, r_id: int, total_amount: float) -> tuple[float, float, bool]:
    # Get restaurant discount settings
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.R_ID == r_id).first()
    if not restaurant or not restaurant.is_discount_active:
        return 0.0, total_amount, False
        
    current_time = datetime.now().time()
    st = restaurant.discount_start_time
    et = restaurant.discount_end_time
    
    if st is None or et is None:
        return 0.0, total_amount, False

    is_applicable = False
    if st < et:
        # Normal range e.g. 10:00 to 14:00
        if st <= current_time <= et:
            is_applicable = True
    else:
        # Crosses midnight e.g. 22:00 to 06:00
        if current_time >= st or current_time <= et:
            is_applicable = True
            
    if is_applicable:
        discount_amount = total_amount * (restaurant.discount_percentage / 100.0)
        final_amount = total_amount - discount_amount
        return discount_amount, final_amount, True
        
    return 0.0, total_amount, False

# In-memory cart: carts[customer_id] = {"r_id": restaurant_id, "items": {food_id: quantity}}
in_memory_carts = {}

@router.get("/restaurants", response_model=list[schemas.RestaurantResponse])
def browse_restaurants(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    restaurants = db.query(models.Restaurant).all()
    return restaurants

@router.get("/restaurants/{r_id}/menu", response_model=list[schemas.FoodItemResponse])
def view_menu(r_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    menu = db.query(models.FoodItem).filter(models.FoodItem.R_ID == r_id, models.FoodItem.Availability == True).all()
    if not menu:
        raise HTTPException(status_code=404, detail="Restaurant or menu not found")
    return menu

@router.post("/cart", response_model=schemas.CartResponse)
def add_to_cart(item: schemas.CartItemAdd, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    food_item = db.query(models.FoodItem).filter(models.FoodItem.Food_ID == item.Food_ID).first()
    if not food_item or not food_item.Availability:
        raise HTTPException(status_code=404, detail="Food item not found or unavailable")
    
    c_id = current_user.C_ID
    if c_id not in in_memory_carts:
        in_memory_carts[c_id] = {"items": {}} # Removed r_id restriction
        
    cart = in_memory_carts[c_id]
        
    if item.Food_ID in cart["items"]:
        cart["items"][item.Food_ID] += item.Quantity
    else:
        cart["items"][item.Food_ID] = item.Quantity
        
    return get_cart(db, current_user)

@router.put("/cart/{food_id}", response_model=schemas.CartResponse)
def update_cart_item(food_id: int, item: schemas.CartItemAdd, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    c_id = current_user.C_ID
    if c_id not in in_memory_carts or food_id not in in_memory_carts[c_id]["items"]:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    if item.Quantity <= 0:
        del in_memory_carts[c_id]["items"][food_id]
    else:
        in_memory_carts[c_id]["items"][food_id] = item.Quantity
        
    return get_cart(db, current_user)

@router.delete("/cart/{food_id}", response_model=schemas.CartResponse)
def remove_from_cart(food_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    c_id = current_user.C_ID
    if c_id in in_memory_carts and food_id in in_memory_carts[c_id]["items"]:
        del in_memory_carts[c_id]["items"][food_id]
        
    return get_cart(db, current_user)

@router.get("/cart", response_model=schemas.CartResponse)
def get_cart(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    c_id = current_user.C_ID
    if c_id not in in_memory_carts or not in_memory_carts[c_id]["items"]:
        return schemas.CartResponse(items=[], Total_Amount=0.0, Final_Amount=0.0)
        
    cart = in_memory_carts[c_id]
    items_response = []
    
    # Group items by restaurant to calculate discounts correctly
    restaurant_totals = {} # {r_id: total_amount}
    
    for f_id, qty in cart["items"].items():
        food = db.query(models.FoodItem, models.Restaurant).join(models.Restaurant).filter(models.FoodItem.Food_ID == f_id).first()
        food_item, restaurant = food
        subtotal = food_item.Price * qty
        
        if restaurant.R_ID not in restaurant_totals:
            restaurant_totals[restaurant.R_ID] = 0.0
        restaurant_totals[restaurant.R_ID] += subtotal
        
        items_response.append(schemas.CartItemResponse(
            Food_ID=food_item.Food_ID,
            Food_Name=food_item.Food_Name,
            Price=food_item.Price,
            Quantity=qty,
            Subtotal=subtotal,
            R_ID=restaurant.R_ID,
            Restaurant_Name=restaurant.Name
        ))
    
    total_amount = 0.0
    total_discount = 0.0
    total_final = 0.0
    offer_applied = False
    
    for r_id, r_total in restaurant_totals.items():
        d_amt, f_amt, applied = calculate_discount(db, r_id, r_total)
        total_amount += r_total
        total_discount += d_amt
        total_final += f_amt
        if applied:
            offer_applied = True
        
    return schemas.CartResponse(
        items=items_response, 
        Total_Amount=total_amount,
        Discount_Amount=total_discount,
        Final_Amount=total_final,
        Night_Offer_Applied=offer_applied
    )

@router.post("/checkout")
def checkout(checkout_req: schemas.CheckoutRequest, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    c_id = current_user.C_ID
    if c_id not in in_memory_carts or not in_memory_carts[c_id]["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    cart = in_memory_carts[c_id]
    
    # Group items by restaurant
    restaurant_items = {} # {r_id: {food_id: qty}}
    for f_id, qty in cart["items"].items():
        food = db.query(models.FoodItem).filter(models.FoodItem.Food_ID == f_id).first()
        r_id = food.R_ID
        if r_id not in restaurant_items:
            restaurant_items[r_id] = {}
        restaurant_items[r_id][f_id] = qty
        
    orders_created = []
    
    for r_id, items in restaurant_items.items():
        # Calculate totals for this specific restaurant
        r_total = 0.0
        for f_id, qty in items.items():
            food = db.query(models.FoodItem).filter(models.FoodItem.Food_ID == f_id).first()
            r_total += food.Price * qty
            
        discount_amount, final_amount, _ = calculate_discount(db, r_id, r_total)
        
        # 1. Create Order directly in 'Preparing' status (since payment is "made" now)
        new_order = models.Order(
            C_ID=c_id,
            R_ID=r_id,
            Total_Amount=r_total,
            Discount_Amount=discount_amount,
            Final_Amount=final_amount,
            Order_Status="Preparing", # Status starts as Preparing after payment
            Date=date.today(),
            Time=datetime.now().time()
        )
        db.add(new_order)
        db.flush() # Flush to get O_ID for payment
        
        # 2. Create Payment record
        payment_status = "Success"
        if checkout_req.Payment_Mode == "COD":
            payment_status = "Pending"
            
        new_payment = models.Payment(
            O_ID=new_order.O_ID,
            Amount=final_amount,
            Payment_Mode=checkout_req.Payment_Mode,
            Payment_Status=payment_status,
            Date=date.today()
        )
        db.add(new_payment)
        orders_created.append(new_order.O_ID)
        
    db.commit()
    
    # Clear the cart after successful checkout
    del in_memory_carts[c_id]
    
    res_msg = "Payment successful and orders placed!"
    if checkout_req.Payment_Mode == "COD":
        res_msg = "Order placed successfully (Cash on Delivery)!"
        
    return {"message": res_msg, "order_ids": orders_created}

@router.post("/order/{o_id}/cancel")
def cancel_order(o_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    order = db.query(models.Order).filter(models.Order.O_ID == o_id, models.Order.C_ID == current_user.C_ID).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.Order_Status in ["Delivered", "Cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order with status: {order.Order_Status}")
        
    order.Order_Status = "Cancelled"
    db.commit()
    return {"message": "Order cancelled successfully"}

@router.get("/order/{o_id}/status")
def track_order_status(o_id: int, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    order = db.query(models.Order).filter(models.Order.O_ID == o_id, models.Order.C_ID == current_user.C_ID).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return {"O_ID": order.O_ID, "Order_Status": order.Order_Status}

@router.get("/orders", response_model=list[schemas.OrderHistoryResponse])
def get_order_history(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["customer"]))):
    c_id = current_user.C_ID
    # Join with Restaurant to get the name
    orders = db.query(models.Order, models.Restaurant).join(models.Restaurant).filter(models.Order.C_ID == c_id).order_by(models.Order.Date.desc(), models.Order.Time.desc()).all()
    
    history = []
    for order, restaurant in orders:
        history.append({
            "O_ID": order.O_ID,
            "Restaurant_Name": restaurant.Name,
            "Final_Amount": order.Final_Amount,
            "Order_Status": order.Order_Status,
            "Date": str(order.Date)
        })
    return history
