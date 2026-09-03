async function renderOrders() {
    const container = document.getElementById("ordersContainer");
    if(!container) return; // Only run on orders page

    if (!currentUser) {
        container.innerHTML = "Bitte melde dich an, um deine Bestellungen zu sehen.";
        return;
    }

    try {
        const orders = await api("/api/orders/my");
        if (orders.length === 0) {
            container.innerHTML = "Du hast noch keine Bestellungen aufgegeben.";
            return;
        }

        container.innerHTML = "";
        orders.forEach(order => {
            const card = document.createElement("div");
            card.className = "order-card";

            let itemsHtml = order.items.map(i => `
                <div class="order-item-detail">
                    <strong>${i.product_name}</strong>
                    <br><small>Größe: ${i.size || '-'} | Farbe: ${i.color || '-'}</small>
                </div>
            `).join('');

            card.innerHTML = `
                <div class="order-card-top">
                    <div>
                        <div class="order-number">${order.order_number}</div>
                        <div class="order-date">${new Date(order.created_at).toLocaleDateString()}</div>
                    </div>
                    <div class="status-badge">${order.status}</div>
                </div>
                <div class="order-card-products">
                    ${itemsHtml}
                </div>
            `;
            container.appendChild(card);
        });
    } catch(e) {
        container.innerHTML = "Fehler beim Laden der Bestellungen.";
    }
}

if(window.location.pathname.includes('orders.html')) {
    const oldOnUserLoaded = window.onUserLoaded;
    window.onUserLoaded = async () => {
        if(oldOnUserLoaded) await oldOnUserLoaded();
        await renderOrders();
    };
}
