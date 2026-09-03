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


async function editCartItem(id) {
    const item = cart.find(i => i.id === id);
    if(!item) return;

    const newName = prompt("Produktname:", item.product_name);
    if(newName === null) return;

    const newSize = prompt("Größe:", item.size || "");
    if(newSize === null) return;

    const newColor = prompt("Farbe:", item.color || "");
    if(newColor === null) return;

    const newNotes = prompt("Notizen:", item.notes || "");
    if(newNotes === null) return;

    try {
        await api(`/api/cart/items/${id}`, {
            method: "PATCH",
            body: JSON.stringify({
                product_name: newName,
                size: newSize,
                color: newColor,
                notes: newNotes
            })
        });
        showToast("Artikel aktualisiert", "success");
        await loadCart();
    } catch(e) {
        showToast(e.message, "error");
    }
}
