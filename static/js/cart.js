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
        throw new Error(
            data?.detail || "Fehler beim Warenkorb."
        );
    }
    return data;
}
async function loadCart() {
    try {
        const data = await cartRequest("/cart");
        updateCartBadge(data.items.length);
        return data.items;
    } catch {
        updateCartBadge(0);
        return [];
    }
}
function updateCartBadge(count) {
    document
        .querySelectorAll("[data-cart-count]")
        .forEach((element) => {
            element.textContent = count;
            element.hidden = count === 0;
        });
}
function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}
function renderCart(items) {
    const container =
        document.querySelector("[data-cart-list]");
    const empty =
        document.querySelector("[data-cart-empty]");
    if (!container) {
        return;
    }
    container.innerHTML = "";
    if (!items.length) {
        if (empty) {
            empty.hidden = false;
        }
        return;
    }
    if (empty) {
        empty.hidden = true;
    }
    items.forEach((item) => {
        const article =
            document.createElement("article");
        article.className = "cart-item";
        article.innerHTML = `
            <div class="cart-item-content">
                <h3>${escapeHtml(item.product_name)}</h3>
                ${
                    item.size
                        ? `<p><strong>Größe:</strong> ${escapeHtml(item.size)}</p>`
                        : ""
                }
                ${
                    item.color
                        ? `<p><strong>Farbe:</strong> ${escapeHtml(item.color)}</p>`
                        : ""
                }
                ${
                    item.notes
                        ? `<p><strong>Notiz:</strong> ${escapeHtml(item.notes)}</p>`
                        : ""
                }
                ${
                    item.product_link
                        ? `<a href="${escapeHtml(item.product_link)}"
                              target="_blank"
                              rel="noopener noreferrer">
                              Produkt öffnen
                           </a>`
                        : ""
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
    container
        .querySelectorAll("[data-remove-cart]")
        .forEach((button) => {
            button.addEventListener(
                "click",
                async () => {
                    const id =
                        button.dataset.removeCart;
                    try {
                        await cartRequest(
                            `/cart/items/${id}`,
                            {
                                method: "DELETE",
                            }
                        );
                        await refreshCart();
                    } catch (error) {
                        alert(error.message);
                    }
                }
            );
        });
}
async function refreshCart() {
    const items = await loadCart();
    renderCart(items);
}
async function checkout() {
    const button =
        document.querySelector("[data-checkout]");
    if (button) {
        button.disabled = true;
        button.textContent = "Wird übermittelt …";
    }
    try {
        const result =
            await cartRequest(
                "/orders/checkout",
                {
                    method: "POST",
                }
            );
        window.location.href =
            `bestellungen.html?order=${result.order_id}`;
    } catch (error) {
        alert(error.message);
        if (button) {
            button.disabled = false;
            button.textContent =
                "Bestellung abschicken";
        }
    }
}
document.addEventListener("DOMContentLoaded", async () => {
    await refreshCart();
    document
        .querySelector("[data-checkout]")
        ?.addEventListener(
            "click",
            checkout
        );
});
