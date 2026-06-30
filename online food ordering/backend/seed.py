import database
import models
import auth
from datetime import time

def seed_data():
    db = database.SessionLocal()
    
    # Check if data already exists
    if db.query(models.Admin).first():
        print("Database already seeded!")
        return

    print("Seeding sample data...")

    # 1. Create Admin
    admin_pw = auth.get_password_hash("admin123")
    admin = models.Admin(Name="System Admin", Email="admin@example.com", Password=admin_pw)
    db.add(admin)

    # 2. Create Restaurants
    rest_pw = auth.get_password_hash("rest123")
    
    # Restaurant 1: The Burger House
    r1 = models.Restaurant(
        Name="The Burger House",
        Email="burger@example.com",
        Password=rest_pw,
        Location="Connaught Place",
        Phone_Number="9876543210",
        Rating=4.5,
        discount_percentage=10.0,
        discount_start_time=time(20, 0), # 8 PM
        discount_end_time=time(23, 59),
        is_discount_active=True
    )
    
    # Restaurant 2: Pizza Palace
    r2 = models.Restaurant(
        Name="Pizza Palace",
        Email="pizza@example.com",
        Password=rest_pw,
        Location="Saket",
        Phone_Number="9876543211",
        Rating=4.2
    )
    
    # Restaurant 3: Spice Symphony (Biryani & Mughlai)
    r3 = models.Restaurant(
        Name="Spice Symphony",
        Email="spice@example.com",
        Password=rest_pw,
        Location="Hauz Khas",
        Phone_Number="9876543212",
        Rating=4.7
    )
    
    db.add_all([r1, r2, r3])
    db.commit()
    db.refresh(r1)
    db.refresh(r2)
    db.refresh(r3)

    # 3. Create Food Items for each
    foods = [
        # Burgers
        models.FoodItem(R_ID=r1.R_ID, Food_Name="Classic Veg Burger", Category="Burgers", Price=120.0, Availability=True),
        models.FoodItem(R_ID=r1.R_ID, Food_Name="Aloo Tikki Burger", Category="Burgers", Price=150.0, Availability=True),
        models.FoodItem(R_ID=r1.R_ID, Food_Name="Cheese Lava Burger", Category="Burgers", Price=220.0, Availability=True),
        models.FoodItem(R_ID=r1.R_ID, Food_Name="Masala Fries", Category="Sides", Price=90.0, Availability=True),
        models.FoodItem(R_ID=r1.R_ID, Food_Name="Cold Coffee", Category="Drinks", Price=110.0, Availability=True),
        
        # Pizza
        models.FoodItem(R_ID=r2.R_ID, Food_Name="Margherita Pizza", Category="Pizza", Price=250.0, Availability=True),
        models.FoodItem(R_ID=r2.R_ID, Food_Name="Farmhouse Pizza", Category="Pizza", Price=380.0, Availability=True),
        models.FoodItem(R_ID=r2.R_ID, Food_Name="Paneer Tikka Pizza", Category="Pizza", Price=450.0, Availability=True),
        models.FoodItem(R_ID=r2.R_ID, Food_Name="Garlic Breadsticks", Category="Sides", Price=140.0, Availability=True),
        models.FoodItem(R_ID=r2.R_ID, Food_Name="Pepsi (500ml)", Category="Drinks", Price=60.0, Availability=True),
        
        # Biryani & More
        models.FoodItem(R_ID=r3.R_ID, Food_Name="Hyderabadi Veg Biryani", Category="Biryani", Price=280.0, Availability=True),
        models.FoodItem(R_ID=r3.R_ID, Food_Name="Lucknowi Paneer Biryani", Category="Biryani", Price=320.0, Availability=True),
        models.FoodItem(R_ID=r3.R_ID, Food_Name="Shahi Paneer", Category="Mughlai", Price=350.0, Availability=True),
        models.FoodItem(R_ID=r3.R_ID, Food_Name="Butter Naan", Category="Breads", Price=60.0, Availability=True),
        models.FoodItem(R_ID=r3.R_ID, Food_Name="Masala Chai", Category="Drinks", Price=40.0, Availability=True),
    ]
    db.add_all(foods)
    
    # 4. Create a Customer
    cust_pw = auth.get_password_hash("cust123")
    customer = models.Customer(
        Name="Amit Kumar",
        Email="customer@example.com",
        Password=cust_pw,
        Mobile_No="9988776655",
        Address="Flat 402, Green Apartments",
        City="New Delhi",
        Pincode="110001"
    )
    db.add(customer)

    # 5. Create Delivery Personnel
    del_pw = auth.get_password_hash("del123")
    d1 = models.DeliveryPerson(Name="Rajesh Delivery", Email="delivery@example.com", Password=del_pw, Phone_Number="9000000001", Availability=True)
    d2 = models.DeliveryPerson(Name="Suresh Fast", Email="fast@example.com", Password=del_pw, Phone_Number="9000000002", Availability=True)
    db.add_all([d1, d2])
    
    db.commit()
    print("Sample data seeded successfully!")
    print("--------------------------------------------------")
    print("ADMIN: admin@example.com / admin123")
    print("CUSTOMER: customer@example.com / cust123")
    print("RESTAURANTS (PW: rest123): burger@example.com, pizza@example.com")
    print("DELIVERY (PW: del123): delivery@example.com, fast@example.com")
    print("--------------------------------------------------")

if __name__ == "__main__":
    # Ensure tables exist
    models.Base.metadata.create_all(bind=database.engine)
    seed_data()
