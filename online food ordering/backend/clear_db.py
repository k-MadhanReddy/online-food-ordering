import database
import models
from sqlalchemy import text

def clear_data():
    db = database.SessionLocal()
    print("Clearing existing data...")
    # Disable foreign key checks for SQLite
    db.execute(text("PRAGMA foreign_keys = OFF;"))
    
    # Delete all records from all tables
    db.query(models.Payment).delete()
    db.query(models.Order).delete()
    db.query(models.FoodItem).delete()
    db.query(models.Restaurant).delete()
    db.query(models.Customer).delete()
    db.query(models.Admin).delete()
    db.query(models.Discount).delete()
    
    db.commit()
    print("Data cleared.")

if __name__ == "__main__":
    clear_data()
