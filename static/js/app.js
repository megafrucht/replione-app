let currentUser = null;
let cart = [];

const STATUS_STEPS = ['Eingegangen', 'In Bearbeitung', 'Bestellt', 'Unterwegs', 'Abgeschlossen'];

function saveCart() { try { localStorage.setItem("replione_cart", JSON.stringify(cart)); } catch (e) {} }
function loadCart() {
    try {
        const saved = localStorage.getItem("replione_cart");
        if (saved) cart = JSON.parse(saved);
    } catch (e) { cart = []; }
    updateCartBadges();
}
function updateCartBadges() {
    const b = document.getElementById("headerCartBadge");
    if (b) b.textContent = cart.length;
}

async function loadCurrentUser() {
    try {
        const res = await fetch("/api/auth/me");
        if (res.ok) {
            currentUser = await res.json();
            const navAccount = document.getElementById("navAccount");
            if (navAccount) navAccount.textContent = "👤 " + currentUser.name.split(" ")[0];
            const navAccountMobile = document.getElementById("navAccountMobile");
            if (navAccountMobile) navAccountMobile.textContent = "👤 " + currentUser.name.split(" ")[0];
        } else {
            currentUser = null;
        }
    } catch (e) { currentUser = null; }
    if (typeof onUserLoaded === "function") onUserLoaded();
}

function showToast(msg) {
    let t = document.getElementById("toast");
    if (!t) {
        t = document.createElement("div");
        t.id = "toast";
        t.className = "toast";
        document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add("show");
    setTimeout(() => t.classList.remove("show"), 3000);
}

document.addEventListener("DOMContentLoaded", () => {
    loadCart();
    loadCurrentUser();
});
