const API_BASE = "/api";
let cart = [];
let currentUser = null;

// Page Navigation
function showPage(page) {
    document.querySelectorAll(".page").forEach(el => el.classList.remove("active"));
    const target = document.getElementById(page);
    if (target) {
        target.classList.add("active");
        window.scrollTo({ top: 0, behavior: "smooth" });
        if (page === "orders") loadOrders();
        if (page === "account") updateAccountUI();
    }
}

// Mobile Menu
function toggleMobileMenu() {
    document.getElementById("mobileMenu").classList.toggle("open");
    document.getElementById("mobileMenuButton").classList.toggle("open");
}
function mobileNavigate(page) { toggleMobileMenu(); showPage(page); }
function mobileOpenCart() { toggleMobileMenu(); openCart(); }

// Auth & API
async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("token");
    const headers = { "Content-Type": "application/json", ...options.headers };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return fetch(API_BASE + endpoint, { ...options, headers });
}

async function checkAuth() {
    try {
        const res = await apiFetch("/auth/me");
        if (res.ok) {
            const data = await res.json();
            currentUser = data.user;
            await loadBackendCart();
        } else {
            currentUser = null;
        }
    } catch { currentUser = null; }
    updateAccountUI();
}

// UI Updates
function updateAccountUI() {
    if (currentUser) {
        document.getElementById("accountLoggedIn").style.display = "block";
        document.getElementById("accountLoggedOut").style.display = "none";
        document.getElementById("accountUserStatus").innerText = "Angemeldet als " + currentUser.name;
    } else {
        document.getElementById("accountLoggedIn").style.display = "none";
        document.getElementById("accountLoggedOut").style.display = "block";
    }
}
function switchAccountTab(tab) {
    document.getElementById("loginForm").style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById("registerForm").style.display = tab === 'register' ? 'block' : 'none';
    document.getElementById("loginTab").classList.toggle("active", tab === 'login');
    document.getElementById("registerTab").classList.toggle("active", tab === 'register');
}

// Auth Actions
async function loginUser(e) {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    try {
        const res = await apiFetch("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        localStorage.setItem("token", data.token);
        await checkAuth();
        showToast("Erfolgreich angemeldet!");
        showPage("home");
    } catch (err) { alert(err.message); }
}

async function registerUser(e) {
    e.preventDefault();
    const name = document.getElementById("registerName").value;
    const email = document.getElementById("registerEmail").value;
    const password = document.getElementById("registerPassword").value;
    try {
        const res = await apiFetch("/auth/register", { method: "POST", body: JSON.stringify({ name, email, password }) });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        localStorage.setItem("token", data.token);
        await checkAuth();
        showToast("Konto erstellt!");
        showPage("home");
    } catch (err) { alert(err.message); }
}

function logoutUser() {
    localStorage.removeItem("token");
    currentUser = null;
    cart = [];
    updateAccountUI();
    renderCartBadges();
    showToast("Abgemeldet");
}

// Cart Logic
async function loadBackendCart() {
    if (!currentUser) return;
    const res = await apiFetch("/cart");
    if (res.ok) {
        cart = await res.json();
        renderCartBadges();
    }
}

function renderCartBadges() {
    document.getElementById("headerCartBadge").innerText = cart.length;
    document.getElementById("mobileCartCount").innerText = `(${cart.length})`;
}

async function addToCart() {
    if (!currentUser) {
        showToast("Bitte logge dich zuerst ein!");
        showPage("account");
        return;
    }
    const size = document.getElementById("size").value;
    const color = document.getElementById("colorText").value;
    if (!size || !color) return showToast("Größe und Farbe fehlen!");
    
    const item = {
        link: document.getElementById("productLink").value,
        size, color,
        notes: document.getElementById("notes").value,
        image_base64: document.getElementById("preview").src.startsWith("data:") ? document.getElementById("preview").src : null
    };

    const res = await apiFetch("/cart/add", { method: "POST", body: JSON.stringify(item) });
    if (res.ok) {
        showToast("Zum Warenkorb hinzugefügt!");
        document.getElementById("size").value = "";
        document.getElementById("colorText").value = "";
        document.getElementById("preview").style.display = "none";
        document.getElementById("screenshot").value = "";
        await loadBackendCart();
    }
}

async function removeFromCart(id) {
    await apiFetch(`/cart/${id}`, { method: "DELETE" });
    await loadBackendCart();
    openCart();
}

// Cart Modal
function openCart() {
    const container = document.getElementById("modalCartItems");
    if (cart.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding:30px; color:#888;">Warenkorb leer.</div>';
        document.getElementById("modalCheckout").style.display = "none";
    } else {
        container.innerHTML = cart.map((p, i) => `
            <div class="cart-item">
                <div class="cart-image">${p.image ? `<img src="${p.image}">` : 'Kein Bild'}</div>
                <div>
                    <h3 style="font-size:16px; margin-bottom:5px;">Produkt ${i+1}</h3>
                    <p style="font-size:13px; color:#555;">Größe: ${p.size} | Farbe: ${p.color}</p>
                </div>
                <button class="remove-button" onclick="removeFromCart(${p.id})">Entfernen</button>
            </div>
        `).join("");
        document.getElementById("modalCheckout").style.display = "block";
    }
    document.getElementById("cartModal").classList.add("open");
}
function closeCart() { document.getElementById("cartModal").classList.remove("open"); }
function closeCartOutside(e) { if(e.target.id === "cartModal") closeCart(); }

// Checkout
async function submitOrder() {
    document.getElementById("modalCheckout").innerText = "Sende...";
    document.getElementById("modalCheckout").disabled = true;
    try {
        const res = await apiFetch("/checkout", { method: "POST" });
        if (!res.ok) throw new Error("Warenkorb ist leer oder Fehler beim Bestellen.");
        const data = await res.json();
        showToast("Bestellung erfolgreich: " + data.order_number);
        cart = [];
        renderCartBadges();
        closeCart();
        showPage("orders");
    } catch (err) {
        alert(err.message);
    } finally {
        document.getElementById("modalCheckout").innerText = "Zahlungspflichtig bestellen";
        document.getElementById("modalCheckout").disabled = false;
    }
}

// Orders
async function loadOrders() {
    if (!currentUser) return;
    const res = await apiFetch("/orders/my");
    if (res.ok) {
        const data = await res.json();
        const container = document.getElementById("ordersContainer");
        if(data.orders.length === 0) {
            container.innerHTML = '<div class="empty-orders">Du hast noch keine Bestellungen.</div>';
        } else {
            container.innerHTML = data.orders.map(o => `
                <div class="order-card" style="margin-bottom:15px;">
                    <div class="order-card-top">
                        <div class="order-number">${o.order_number}</div>
                        <div class="order-status">${o.status}</div>
                    </div>
                    <div style="font-size:13px; color:#555; margin-top:10px;">${o.items.length} Produkte | Datum: ${o.created_at.split("T")[0]}</div>
                </div>
            `).join("");
        }
    }
}

// Utils
function showToast(msg) {
    const toast = document.getElementById("toast");
    toast.innerText = msg;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3000);
}

function updateSummary() {
    document.getElementById("summaryLink").innerText = document.getElementById("productLink").value || "Nicht angegeben";
    document.getElementById("summarySize").innerText = document.getElementById("size").value || "—";
    document.getElementById("summaryColor").innerText = document.getElementById("colorText").value || "—";
}

function previewImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) return showToast("Bild maximal 5MB groß");
    const reader = new FileReader();
    reader.onload = e => {
        document.getElementById("preview").src = e.target.result;
        document.getElementById("preview").style.display = "block";
    };
    reader.readAsDataURL(file);
}

// Start
checkAuth();
