const API_BASE = "/api";
let cart = [];
let currentUser = null;

// Cart Persistence
function saveCart() {
    try { localStorage.setItem("replione_cart", JSON.stringify(cart)); } catch (e) {}
}

function loadCart() {
    try {
        const saved = localStorage.getItem("replione_cart");
        if (saved) cart = JSON.parse(saved);
    } catch (e) { cart = []; }
    updateCartBadges();
}

function updateCartBadges() {
    const badge = document.getElementById("headerCartBadge");
    const mobileCount = document.getElementById("mobileCartCount");
    if (badge) badge.textContent = cart.length;
    if (mobileCount) mobileCount.textContent = `(${cart.length})`;
}

// User Context
async function loadCurrentUser() {
    try {
        const response = await apiFetch("/auth/me");
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user || null;
        } else {
            currentUser = null;
        }
    } catch (e) {
        currentUser = null;
    }
    if (typeof onUserLoaded === "function") onUserLoaded();
}

// Helpers
async function apiFetch(endpoint, options = {}) {
    return fetch(API_BASE + endpoint, {
        ...options,
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        credentials: "include"
    });
}

async function getErrorMessage(response) {
    try {
        const data = await response.json();
        return data.detail || data.message || "Serverfehler.";
    } catch {
        return "Serverfehler.";
    }
}

function escapeHTML(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

let toastTimer;
function showToast(message) {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.className = "toast";
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 3000);
}

// Mobile Menu
function toggleMobileMenu() {
    document.getElementById("mobileMenu").classList.toggle("open");
    document.getElementById("mobileMenuButton").classList.toggle("open");
}

// Cart Modal
function openCart() {
    renderModalCart();
    document.getElementById("cartModal").classList.add("open");
}
function closeCart() {
    document.getElementById("cartModal").classList.remove("open");
}
function closeCartOutside(e) {
    if (e.target.id === "cartModal") closeCart();
}

function renderModalCart() {
    const container = document.getElementById("modalCartItems");
    if (!container) return;
    if (cart.length === 0) {
        container.innerHTML = `<div class="cart-empty">Dein Warenkorb ist leer.</div>`;
        return;
    }
    container.innerHTML = "";
    cart.forEach((p, idx) => {
        const item = document.createElement("div");
        item.className = "cart-item";
        item.style.gridTemplateColumns = "65px 1fr";
        item.innerHTML = `
            <div class="cart-image" style="width:65px; height:65px;">
                ${p.image ? `<img src="${escapeHTML(p.image)}" alt="">` : "—"}
            </div>
            <div class="cart-details">
                <h3>Produkt ${idx + 1}</h3>
                <p>Größe: ${escapeHTML(p.size)}</p>
                <p>Farbe: ${escapeHTML(p.color)}</p>
            </div>
        `;
        container.appendChild(item);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    loadCart();
    loadCurrentUser();
});