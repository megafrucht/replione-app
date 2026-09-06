const CART_API = "/api";

async function cartRequest(url, options = {}) {
    const response = await fetch(`${CART_API}${url}`, {
        credentials: "include",
        ...options,
    });

    let data = null;
    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        throw new Error(data?.detail || "Fehler beim Warenkorb.");
    }

    return data;
}

function calculateTotalItems(items) {
    if (!Array.isArray(items)) return 0;
    return items.reduce((sum, item) => {
        const qty = Number(item.quantity || item.amount || item.count || 1);
        return sum + (isNaN(qty) ? 1 : qty);
    }, 0);
}

async function loadCart() {
    try {
        const data = await cartRequest("/cart");
        
        // Fängt Arrays direkt sowie { items: [...] } oder { cart: [...] } flexibel ab
        const items = Array.isArray(data) 
            ? data 
            : (data?.items || data?.cart?.items || data?.cart || []);

        const totalCount = calculateTotalItems(items);
        updateCartBadge(totalCount);
        return items;
    } catch (error) {
        console.error("Fehler beim Laden des Warenkorbs:", error);
        updateCartBadge(0);
        return [];
    }
}

function updateCartBadge(count) {
    const safeCount = Number(count) || 0;

    // Aktualisiert alle Header-Badges
    document.querySelectorAll("[data-cart-count], .cart-count").forEach((element) => {
        element.textContent = safeCount;
        element.hidden = safeCount === 0;
        element.style.display = safeCount === 0 ? "none" : "flex";
    });

    // Aktualisiert die Anzeige im Checkout-Kasten
    const totalItemsElem = document.getElementById("cartTotalItems");
    if (totalItemsElem) {
        totalItemsElem.textContent = safeCount;
    }
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function renderCart(items) {
    const container = document.querySelector("[data-cart-list]");
    const empty = document.querySelector("[data-cart-empty]");

    if (!container) return;

    container.innerHTML = "";

    if (!items || !items.length) {
        if (empty) empty.hidden = false;
        return;
    }

    if (empty) empty.hidden = true;

    items.forEach((item) => {
        const article = document.createElement("article");
        article.className = "cart-item";
        
        const quantityHtml = (item.quantity && item.quantity > 1)
            ? `<p><strong>Menge:</strong> ${escapeHtml(item.quantity)}</p>`
            : "";

        article.innerHTML = `
            <div class="cart-item-content">
                <h3>${escapeHtml(item.product_name || item.name || "Produkt")}</h3>
                ${quantityHtml}
                ${item.size ? `<p><strong>Größe:</strong> ${escapeHtml(item.size)}</p>` : ""}
                ${item.color ? `<p><strong>Farbe:</strong> ${escapeHtml(item.color)}</p>` : ""}
                ${item.notes ? `<p><strong>Notiz:</strong> ${escapeHtml(item.notes)}</p>` : ""}
                ${item.product_link ? `
                    <a href="${escapeHtml(item.product_link)}" target="_blank" rel="noopener noreferrer">
                        Produkt öffnen
                    </a>` : ""
                }
            </div>
            <button
                type="button"
                class="button button-secondary"
                data-remove-cart="${item.id}"
            >
                Entfernen
            </button>
        `;
        container.appendChild(article);
    });

    container.querySelectorAll("[data-remove-cart]").forEach((button) => {
        button.addEventListener("click", async () => {
            const id = button.dataset.removeCart;
            try {
                await cartRequest(`/cart/items/${id}`, { method: "DELETE" });
                await refreshCart();
            } catch (error) {
                alert(error.message);
            }
        });
    });
}

async function refreshCart() {
    const items = await loadCart();
    renderCart(items);
}

async function checkout() {
    const button = document.querySelector("[data-checkout]");
    if (button) {
        button.disabled = true;
        button.textContent = "Wird übermittelt …";
    }

    try {
        const result = await cartRequest("/orders/checkout", { method: "POST" });
        window.location.href = `bestellungen.html?order=${result.order_id}`;
    } catch (error) {
        alert(error.message);
        if (button) {
            button.disabled = false;
            button.textContent = "Bestellung abschicken";
        }
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await refreshCart();
    document.querySelector("[data-checkout]")?.addEventListener("click", checkout);
});
