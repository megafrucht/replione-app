let adminToken = sessionStorage.getItem("admin_access_token");

async function apiAdmin(path, options = {}) {
    options.headers = options.headers || {};
    // Add token if needed, or rely on cookie via credentials
    const fetchOptions = {
        credentials: "include",
        ...options
    };

    const response = await fetch(path, fetchOptions);
    if (!response.ok) {
        if(response.status === 401) {
            document.getElementById('login-overlay').style.display = 'flex';
            document.getElementById('dashboard').style.display = 'none';
        }
        throw new Error("Admin API Error");
    }
    return response.json();
}

async function loginAdmin() {
    const pwd = document.getElementById("admin-password").value;
    try {
        const res = await fetch("/api/admin/login", {
            method: "POST",
            headers: { "x-admin-password": encodeURIComponent(pwd) }
        });
        if (res.ok) {
            document.getElementById('login-overlay').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
            loadAdminData();
        } else {
            alert("Falsches Passwort");
        }
    } catch(e) {
        alert("Error logging in");
    }
}

async function logoutAdmin() {
    await fetch("/api/admin/logout", { method: "POST" });
    location.reload();
}

async function checkAdminAuth() {
    try {
        await apiAdmin("/api/admin/check");
        document.getElementById('login-overlay').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        loadAdminData();
    } catch(e) {
        document.getElementById('login-overlay').style.display = 'flex';
    }
}


let ordersCache = [];

async function loadAdminData() {
    const [users, orders] = await Promise.all([
        apiAdmin("/api/admin/users"),
        apiAdmin("/api/admin/orders")
    ]);
    ordersCache = orders;

    const ut = document.querySelector("#users-table tbody");
    ut.innerHTML = "";
    users.forEach(u => {
        ut.innerHTML += `<tr>
            <td>${u.id}</td>
            <td>${u.name}</td>
            <td>${u.email}</td>
            <td>${new Date(u.created_at).toLocaleDateString()}</td>
            <td>${u.order_count}</td>
        </tr>`;
    });

    const ot = document.querySelector("#orders-table tbody");
    ot.innerHTML = "";
    orders.forEach(o => {
        ot.innerHTML += `<tr>
            <td>${o.id}</td>
            <td>${o.order_number}</td>
            <td>${o.user_name}</td>
            <td>
                <select onchange="updateOrderStatus('${o.order_number}', this.value)">
                    <option value="Eingegangen" ${o.status==='Eingegangen'?'selected':''}>Eingegangen</option>
                    <option value="In Bearbeitung" ${o.status==='In Bearbeitung'?'selected':''}>In Bearbeitung</option>
                    <option value="Bestellt" ${o.status==='Bestellt'?'selected':''}>Bestellt</option>
                    <option value="Unterwegs" ${o.status==='Unterwegs'?'selected':''}>Unterwegs</option>
                    <option value="Abgeschlossen" ${o.status==='Abgeschlossen'?'selected':''}>Abgeschlossen</option>
                </select>
            </td>
            <td>${new Date(o.created_at).toLocaleDateString()}</td>
            <td><button onclick="showOrderDetails('${o.order_number}')">Details</button></td>
        </tr>`;
    });
}

function showOrderDetails(orderNum) {
    const order = ordersCache.find(o => o.order_number === orderNum);
    if(!order) return;

    let modal = document.getElementById("admin-order-modal");
    if(!modal) {
        modal = document.createElement("div");
        modal.id = "admin-order-modal";
        modal.style.cssText = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; display:flex; justify-content:center; align-items:center; padding:20px; overflow-y:auto;";
        document.body.appendChild(modal);
    }

    let itemsHtml = order.items.map(i => `
        <div style="background:#f1f1f1; padding:15px; margin-bottom:10px; border-radius:8px;">
            <strong>${i.product_name}</strong>
            <div style="font-size:14px; margin:5px 0;">
                Größe: ${i.size || '-'} | Farbe: ${i.color || '-'}<br>
                Link: ${i.product_link ? `<a href="${i.product_link}" target="_blank">Öffnen</a>` : '-'}<br>
                Notizen: ${i.notes || '-'}
            </div>
            ${i.screenshot_id ? `<a href="/api/upload/${i.screenshot_id}" target="_blank"><img src="/api/upload/${i.screenshot_id}" style="max-height:150px; cursor:pointer;"></a>` : ''}
        </div>
    `).join('');

    modal.innerHTML = `
        <div style="background:white; padding:20px; border-radius:12px; width:100%; max-width:800px; max-height:90vh; overflow-y:auto;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h2>Details: ${order.order_number}</h2>
                <button onclick="document.getElementById('admin-order-modal').style.display='none'" style="padding:5px 10px; cursor:pointer;">Schließen</button>
            </div>
            <p><strong>Kunde:</strong> ${order.user_name} (${order.user_email})</p>
            <p><strong>Status:</strong> ${order.status}</p>
            <p><strong>Datum:</strong> ${new Date(order.created_at).toLocaleString()}</p>
            <h3>Produkte (${order.items.length})</h3>
            ${itemsHtml}
        </div>
    `;
    modal.style.display = 'flex';
}

async function updateOrderStatus(orderNum, status) {
    try {
        await apiAdmin(`/api/admin/orders/${orderNum}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status })
        });
        alert("Status aktualisiert");
    } catch(e) {
        alert("Fehler beim Aktualisieren");
    }
}

document.addEventListener("DOMContentLoaded", checkAdminAuth);
