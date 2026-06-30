from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import database
import models
import schemas
import auth

router = APIRouter(prefix="/api/delivery", tags=["Delivery Features"])

@router.get("/orders", response_model=list[schemas.DeliveryOrderResponse])
def get_assigned_orders(db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["delivery"]))):
    d_id = current_user.D_ID
    # Get orders assigned to this delivery person that are not yet Delivered or Cancelled
    orders = db.query(models.Order, models.Customer).join(models.Customer).filter(
        models.Order.D_ID == d_id,
        models.Order.Order_Status.in_(["Preparing", "Picked Up", "Out for Delivery"])
    ).all()
    
    response = []
    for order, customer in orders:
        response.append({
            "O_ID": order.O_ID,
            "Customer_Name": customer.Name,
            "Customer_Phone": customer.Mobile_No,
            "Delivery_Address": customer.Address + ", " + customer.City,
            "Total_Amount": order.Final_Amount,
            "Order_Status": order.Order_Status
        })
    return response

@router.put("/order/{o_id}/status")
def update_delivery_status(o_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(database.get_db), current_user = Depends(auth.require_role(["delivery"]))):
    order = db.query(models.Order).filter(models.Order.O_ID == o_id, models.Order.D_ID == current_user.D_ID).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not assigned to you")
        
    allowed_statuses = ["Picked Up", "Out for Delivery", "Delivered"]
    if status_update.Order_Status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {allowed_statuses}")
        
    order.Order_Status = status_update.Order_Status
    if status_update.Order_Status == "Delivered" and order.payment:
        order.payment.Payment_Status = "Success"
    db.commit()
    return {"message": f"Order status updated to {status_update.Order_Status}"}
