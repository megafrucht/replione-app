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


// COMING SOON LOGIC
function checkComingSoon() {
    // Only apply if we're not on admin.html
    if (window.location.pathname.includes('/admin')) return;

    const bypassToken = localStorage.getItem('replione_bypass');
    if (bypassToken === '040926LITlit!€') {
        return; // Authorized
    }

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'coming-soon-overlay';

    overlay.innerHTML = `
        <h1 class="bypass-trigger">Du bist wohl noch etwas zu früh!</h1>
        <p>Am 04.09.2026 erfährst du mehr!</p>
    `;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden'; // Prevent scrolling

    let clickCount = 0;
    let clickTimer;

    const trigger = overlay.querySelector('.bypass-trigger');
    trigger.addEventListener('click', () => {
        clickCount++;
        clearTimeout(clickTimer);

        if (clickCount >= 5) {
            const pwd = prompt("Passwort:");
            if (pwd === '040926LITlit!€') {
                localStorage.setItem('replione_bypass', pwd);
                overlay.remove();
                document.body.style.overflow = '';
            }
            clickCount = 0;
        } else {
            clickTimer = setTimeout(() => {
                clickCount = 0;
            }, 1000);
        }
    });
}

document.addEventListener('DOMContentLoaded', checkComingSoon);
