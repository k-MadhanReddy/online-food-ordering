# Online Food Ordering & Delivery System

A complete full-stack platform with real-time tracking, role-based dashboards, and delivery lifecycle management.

## 🚀 How to Run the System

### 1. Backend Setup (FastAPI + SQLite)
Navigate to the root directory and follow these steps:

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Initialize Database (Fresh Start)**:
    *If you have an existing database, delete `backend/food_delivery.db` first.*
    ```bash
    python backend/seed.py
    ```
3.  **Start the Server**:
    ```bash
    uvicorn backend.main:app --reload
    ```
    *The API will be live at: http://127.0.0.1:8000*

### 2. Frontend Access
Open the following files directly in your browser:
- `frontend/login.html` (Main Entry Point)
- `frontend/register.html` (For new customers)

---

## 🧪 How to Test (Full Lifecycle)

Use these test credentials to verify the entire flow:

| Role | Email | Password | Dashboard |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `admin123` | `admin_dashboard.html` |
| **Customer** | `customer@example.com` | `cust123` | `customer_dashboard.html` |
| **Restaurant** | `burger@example.com` | `rest123` | `restaurant_dashboard.html` |
| **Delivery** | `delivery@example.com` | `del123` | `delivery_dashboard.html` |

### Recommended Test Flow:
1.  **Login as Customer**: Add items from "The Burger House" to your cart and checkout (Choose COD or UPI).
2.  **Login as Restaurant**: View the "Incoming Order", accept it, and mark it as "Ready".
3.  **Login as Admin**: Go to "Manage Active Orders" and assign the order to "Rajesh Delivery".
4.  **Login as Delivery**: See the assigned order, mark it as "Picked Up" -> "Out for Delivery" -> "Delivered".
5.  **Final Check**: Login as **Admin** again to see the revenue from that order reflected in the dashboard summary!

---

## ✨ Features Implemented
- **Multi-Tenant**: Support for multiple restaurants with independent analytics.
- **Role-Based Auth**: Secure JWT authentication for Admins, Customers, Restaurants, and Delivery.
- **Dynamic Cart**: Multi-restaurant cart with automatic order splitting and night discounts.
- **Real-Time Dashboards**: Summary counts and status updates refresh automatically.
- **Data Integrity**: Cascade deletes and backend validation prevent invalid states.
- **Diagnostics**: Detailed console logging for all API requests.
