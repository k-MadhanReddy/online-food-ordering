const API_URL = 'http://127.0.0.1:8000/api';

function setToken(token) {
    localStorage.setItem('token', token);
}

function getToken() {
    return localStorage.getItem('token');
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
}

function checkAuth() {
    if (!getToken()) {
        window.location.href = 'login.html';
    }
}

function getAuthHeaders() {
    return {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
    };
}
