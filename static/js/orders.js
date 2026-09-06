const ORDERS_API = "/api";
async function loadOrders() {
    const response =
        await fetch(
            `${ORDERS_API}/orders`,
            {
                credentials: "include",
            }
        );
    let data = null;
    try {
        data = await response.json();
    } catch {}
    if (!response.ok) {
        throw new Error(
            data?.detail ||
            "Bestellungen konnten nicht geladen werden."
        );
    }
    return data.orders;
}
function escapeOrderHtml(value) {
    const div =
        document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}
function renderOrders(orders) {
    const container =
        document.querySelector(
            "[data-orders-list]"
        );
    const empty =
        document.querySelector(
            "[data-orders-empty]"
        );
    if (!container) {
        return;
    }
    container.innerHTML = "";
    if (!orders.length) {
        if (empty) {
            empty.hidden = false;
        }
        return;
    }
    if (empty) {
        empty.hidden = true;
    }
    orders.forEach((order) => {
        const article =
            document.createElement("article");
        article.className =
            "order-card";
        const date =
            new Date(
                order.created_at
            ).toLocaleDateString(
                "de-DE"
            );
        article.innerHTML = `
            <div class="order-card-header">
                <div>
                    <h3>Bestellung #${order.id}</h3>
                    <p>${date}</p>
                </div>
                <span class="status-badge">
                    ${escapeOrderHtml(order.status)}
                </span>
            </div>
            <div class="order-card-items">
                ${order.items
                    .map(
                        (item) =>
                            `<p>${escapeOrderHtml(
                                item.product_name
                            )}</p>`
                    )
                    .join("")}
            </div>
            <p>
                Zahlung:
                ${escapeOrderHtml(
                    order.payment_method
                )}
                ·
                ${escapeOrderHtml(
                    order.payment_status
                )}
            </p>
        `;
        container.appendChild(article);
    });
}
document.addEventListener(
    "DOMContentLoaded",
    async () => {
        try {
            const orders =
                await loadOrders();
            renderOrders(orders);
        } catch (error) {
            const container =
                document.querySelector(
                    "[data-orders-list]"
                );
            if (container) {
                container.innerHTML = `
                    <div class="message error">
                        ${escapeOrderHtml(
                            error.message
                        )}
                    </div>
                `;
            }
        }
    }
);
