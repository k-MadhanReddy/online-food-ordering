const API_URL = 'http://127.0.0.1:8000/api';
let token = null;

// DOM Elements
const loginBtn = document.getElementById('login-btn');
const mainContent = document.getElementById('main-content');
const authStatus = document.getElementById('auth-status');
const restaurantsList = document.getElementById('restaurants-list');
const menuSection = document.getElementById('menu-section');
const menuList = document.getElementById('menu-list');

// Cart Elements
const cartItemsContainer = document.getElementById('cart-items');
const cartSummary = document.getElementById('cart-summary');
const cartSubtotal = document.getElementById('cart-subtotal');
const cartTotal = document.getElementById('cart-total');
const nightOfferBadge = document.getElementById('night-offer-badge');
const discountAmountSpan = document.getElementById('discount-amount');
const placeOrderBtn = document.getElementById('place-order-btn');

// 1. Mock Login (For demo purposes, we assume a customer exists or we register one on the fly)
loginBtn.addEventListener('click', async () => {
    loginBtn.textContent = 'Logging in...';
    try {
        // We will attempt to login with a mock user. If it fails, we register them first.
        const mockEmail = 'demo@example.com';
        const mockPassword = 'password123';
        
        let loginRes = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: mockEmail, password: mockPassword, role: 'customer' })
        });

        if (!loginRes.ok) {
            // Register first
            await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    Name: 'Demo Customer', Email: mockEmail, Password: mockPassword,
                    Mobile_No: '1234567890', Address: '123 Main St', City: 'City', Pincode: '12345'
                })
            });
            // Try login again
            loginRes = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: mockEmail, password: mockPassword, role: 'customer' })
            });
        }
        
        const data = await loginRes.json();
        token = data.access_token;
        
        authStatus.innerHTML = '<span style="color:var(--success); font-weight:bold;">✅ Logged in</span>';
        mainContent.classList.remove('hidden');
        
        loadRestaurants();
        loadCart();
    } catch (e) {
        alert('Login failed. Ensure backend is running.');
        loginBtn.textContent = 'Login as Customer';
    }
});

async function loadRestaurants() {
    const res = await fetch(`${API_URL}/customer/restaurants`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const restaurants = await res.json();
    
    if (restaurants.length === 0) {
        restaurantsList.innerHTML = '<p>No restaurants found. Please add some via Admin API.</p>';
        return;
    }

    restaurantsList.innerHTML = restaurants.map(r => `
        <div class="card">
            <h3>${r.Name}</h3>
            <p>📍 ${r.Location}</p>
            <button class="btn-small" onclick="loadMenu(${r.R_ID}, '${r.Name}')">View Menu</button>
        </div>
    `).join('');
}

async function loadMenu(r_id, r_name) {
    const res = await fetch(`${API_URL}/customer/restaurants/${r_id}/menu`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const menu = await res.json();
    
    menuSection.classList.remove('hidden');
    menuSection.querySelector('h2').textContent = `Menu - ${r_name}`;
    
    if (menu.length === 0) {
        menuList.innerHTML = '<p>No menu items available.</p>';
        return;
    }

    menuList.innerHTML = menu.map(item => `
        <div class="card">
            <h3>${item.Food_Name}</h3>
            <p>${item.Category} • ₹${item.Price.toFixed(2)}</p>
            <button class="btn-small" style="background:var(--primary)" onclick="addToCart(${item.Food_ID})">Add to Cart</button>
        </div>
    `).join('');
}

async function addToCart(food_id) {
    await fetch(`${API_URL}/customer/cart`, {
        method: 'POST',
        headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ Food_ID: food_id, Quantity: 1 })
    });
    loadCart();
}

async function loadCart() {
    const res = await fetch(`${API_URL}/customer/cart`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const cart = await res.json();
    
    if (!cart.items || cart.items.length === 0) {
        cartItemsContainer.innerHTML = '<p class="empty-cart-msg">Your cart is empty.</p>';
        cartSummary.classList.add('hidden');
        return;
    }

    cartSummary.classList.remove('hidden');
    cartItemsContainer.innerHTML = cart.items.map(item => `
        <div class="cart-item">
            <span>${item.Quantity}x ${item.Food_Name}</span>
            <span>₹${item.Subtotal.toFixed(2)}</span>
        </div>
    `).join('');

    cartSubtotal.textContent = `₹${cart.Total_Amount.toFixed(2)}`;
    cartTotal.textContent = `₹${cart.Final_Amount.toFixed(2)}`;

    // Show Night Offer if applied
    if (cart.Night_Offer_Applied) {
        nightOfferBadge.classList.remove('hidden');
        discountAmountSpan.textContent = `-₹${cart.Discount_Amount.toFixed(2)}`;
    } else {
        nightOfferBadge.classList.add('hidden');
    }
}

placeOrderBtn.addEventListener('click', async () => {
    const res = await fetch(`${API_URL}/customer/order`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (res.ok) {
        alert('Order placed successfully!');
        loadCart(); // Will reload empty cart
    } else {
        alert('Failed to place order');
    }
});
