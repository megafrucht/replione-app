document.addEventListener("DOMContentLoaded", () => {

    const STORAGE_KEY = "replione_demo_cart";


    function getCart() {

        try {
            return JSON.parse(
                localStorage.getItem(STORAGE_KEY)
            ) || [];
        } catch {
            return [];
        }

    }


    function saveCart(cart) {

        localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify(cart)
        );

    }


    function updateCartBadges() {

        const cart = getCart();

        document.querySelectorAll(".cart-count").forEach((badge) => {
            badge.textContent = cart.length;
        });

    }


    function escapeHTML(value) {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");

    }


    function renderCartPage() {

        const container = document.getElementById("cartItems");

        if (!container) {
            return;
        }


        const emptyCart = document.getElementById("emptyCart");

        const totalItems = document.getElementById("cartTotalItems");

        const cart = getCart();


        if (totalItems) {
            totalItems.textContent = cart.length;
        }


        if (cart.length === 0) {

            container.innerHTML = "";

            if (emptyCart) {
                emptyCart.hidden = false;
            }

            return;
        }


        if (emptyCart) {
            emptyCart.hidden = true;
        }


        container.innerHTML = cart.map((item, index) => {

            const image = item.image || "";

            return `
                <article class="cart-item">

                    <div class="cart-item-image">

                        ${
                            image
                                ? `<img src="${image}" alt="Produkt Screenshot">`
                                : `<span style="font-size:40px;display:flex;align-items:center;justify-content:center;height:100%;">📦</span>`
                        }

                    </div>


                    <div class="cart-item-info">

                        <h3>
                            ${escapeHTML(item.name)}
                        </h3>

                        <p>
                            ${escapeHTML(item.notes || "Keine zusätzlichen Hinweise")}
                        </p>


                        <div class="cart-item-meta">

                            ${
                                item.size
                                    ? `<span class="meta-tag">Größe: ${escapeHTML(item.size)}</span>`
                                    : ""
                            }

                            ${
                                item.color
                                    ? `<span class="meta-tag">Farbe: ${escapeHTML(item.color)}</span>`
                                    : ""
                            }

                            ${
                                item.link
                                    ? `<span class="meta-tag">Link vorhanden</span>`
                                    : ""
                            }

                        </div>

                    </div>


                    <button
                        class="cart-item-remove"
                        data-index="${index}"
                        aria-label="Produkt entfernen"
                    >
                        ✕
                    </button>

                </article>
            `;

        }).join("");


        container
            .querySelectorAll(".cart-item-remove")
            .forEach((button) => {

                button.addEventListener("click", () => {

                    const index = Number(button.dataset.index);

                    removeFromCart(index);

                });

            });

    }


    function removeFromCart(index) {

        const cart = getCart();

        cart.splice(index, 1);

        saveCart(cart);

        updateCartBadges();

        renderCartPage();

    }


    window.replioneCart = {

        getCart,
        saveCart,
        updateCartBadges,
        renderCartPage

    };


    updateCartBadges();

    renderCartPage();

});
