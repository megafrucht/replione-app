let cart = [];

async function loadCart() {
    if (currentUser) {
        try {
            cart = await api("/api/cart");
        } catch (e) {
            cart = [];
        }
    } else {
        cart = [];
    }
    updateCartBadges();
    if (typeof renderCart === "function") {
        renderCart();
    }
}

async function addToCart(item) {
    if (!currentUser) {
        showToast("Bitte melde dich zuerst an.", "error");
        setTimeout(() => window.location.href = "/account.html", 700);
        return false;
    }
    try {
        await api("/api/cart/items", {
            method: "POST",
            body: JSON.stringify(item)
        });
        showToast("Zum Warenkorb hinzugefügt!", "success");
        await loadCart();
        return true;
    } catch(e) {
        showToast(e.message, "error");
        return false;
    }
}

async function removeFromCart(id) {
    try {
        await api(`/api/cart/items/${id}`, { method: 'DELETE' });
        showToast("Artikel entfernt", "success");
        await loadCart();
    } catch(e) {
        showToast(e.message, "error");
    }
}

function updateCartBadges() {
    const badges = document.querySelectorAll("#headerCartBadge");
    badges.forEach(b => {
        b.textContent = cart.length;
    });
}
