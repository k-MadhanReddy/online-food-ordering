from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import database
import models
from routes import auth_routes, customer_routes, restaurant_routes, admin_routes, delivery_routes

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Online Food Ordering API")

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["null", "http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_routes.router)
app.include_router(customer_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(admin_routes.router)
app.include_router(delivery_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Online Food Ordering API"}

@app.get("/health")
def health_check(db: Session = Depends(database.get_db)):
    # simple check to see if DB is accessible
    return {"status": "ok", "database": "connected"}
