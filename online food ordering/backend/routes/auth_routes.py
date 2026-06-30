from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import database
import models
import schemas
import auth

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.CustomerResponse)
def register_customer(customer: schemas.CustomerCreate, db: Session = Depends(database.get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.Email == customer.Email).first()
    if db_customer:
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

@router.post("/login", response_model=schemas.Token)
def login(login_req: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = None
    if login_req.role == "customer":
        user = db.query(models.Customer).filter(models.Customer.Email == login_req.email).first()
    elif login_req.role == "restaurant":
        user = db.query(models.Restaurant).filter(models.Restaurant.Email == login_req.email).first()
    elif login_req.role == "admin":
        user = db.query(models.Admin).filter(models.Admin.Email == login_req.email).first()
    elif login_req.role == "delivery":
        user = db.query(models.DeliveryPerson).filter(models.DeliveryPerson.Email == login_req.email).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid role specified")

    if not user or not auth.verify_password(login_req.password, user.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.Email, "role": login_req.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user = Depends(auth.get_current_user)):
    # Return user details excluding password
    return {
        "email": current_user.Email,
        "name": current_user.Name,
        "role": current_user.role
    }

@router.get("/admin-only")
def admin_only_endpoint(current_user = Depends(auth.require_role(["admin"]))):
    return {"message": "Welcome Admin!"}
