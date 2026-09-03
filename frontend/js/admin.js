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

async function loadAdminData() {
    const [users, orders] = await Promise.all([
        apiAdmin("/api/admin/users"),
        apiAdmin("/api/admin/orders")
    ]);

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
            <td><button onclick="alert('Details für ' + '${o.order_number}')">Details</button></td>
        </tr>`;
    });
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
