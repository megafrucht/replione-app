const API = "/api/admin";
const BASE_API = "/api";

async function apiRequest(url, options = {}) {
    const response = await fetch(`${url.startsWith('/api') ? '' : API}${url}`, {
        credentials: "include",
        ...options,
    });
    let data = null;
    try { data = await response.json(); } catch {}
    if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
            if (!window.location.pathname.endsWith("login.html")) {
                window.location.href = "login.html";
            }
        }
        throw new Error(data?.detail || "Fehler beim API-Aufruf");
    }
    return data;
}

// Login
const loginForm = document.getElementById("adminLoginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const pwd = document.getElementById("adminPassword").value;
        const msg = document.getElementById("authMessage");
        try {
            const formData = new URLSearchParams();
            formData.append('password', pwd);
            await fetch(`${BASE_API}/auth/admin-login`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData
            }).then(async r => {
                if(!r.ok) { const d = await r.json(); throw new Error(d?.detail || "Login fehlgeschlagen");}
            });
            window.location.href = "index.html";
        } catch (error) {
            msg.textContent = error.message;
            msg.hidden = false;
        }
    });
}

// Check Auth on load
document.addEventListener("DOMContentLoaded", async () => {
    if (window.location.pathname.endsWith("login.html")) return;

    try {
        const user = await fetch(`${BASE_API}/auth/me`, {credentials: "include"}).then(r => r.json());
        if (!user.is_admin) {
            window.location.href = "login.html";
        }
    } catch {
        window.location.href = "login.html";
    }

    if (document.getElementById("ordersTbody")) loadOrders();
    if (document.getElementById("usersTbody")) loadUsers();
});

// Logout
const logoutBtns = [document.getElementById("adminLogoutBtn"), document.getElementById("adminLogoutBtnMobile")];
logoutBtns.forEach(btn => {
    if(btn) btn.addEventListener("click", async (e) => {
        e.preventDefault();
        await fetch(`${BASE_API}/auth/logout`, {method: "POST", credentials: "include"});
        window.location.href = "login.html";
    });
});

let allOrders = [];

async function loadOrders() {
    try {
        const data = await apiRequest("/orders");
        allOrders = data.orders || [];
        updateStats();
        renderOrders();
    } catch (e) {
        document.getElementById("ordersTbody").innerHTML = `<tr><td colspan="6" class="error">${e.message}</td></tr>`;
    }
}

function updateStats() {
    const stats = {
        new: allOrders.filter(o => o.status === "Eingegangen").length,
        progress: allOrders.filter(o => o.status === "In Bearbeitung").length,
        shipped: allOrders.filter(o => o.status === "Unterwegs").length,
        done: allOrders.filter(o => o.status === "Abgeschlossen").length,
        unpaid: allOrders.filter(o => o.payment_status === "offen").length,
    };
    if(document.getElementById("statNew")) document.getElementById("statNew").textContent = stats.new;
    if(document.getElementById("statProgress")) document.getElementById("statProgress").textContent = stats.progress;
    if(document.getElementById("statShipped")) document.getElementById("statShipped").textContent = stats.shipped;
    if(document.getElementById("statDone")) document.getElementById("statDone").textContent = stats.done;
    if(document.getElementById("statUnpaid")) document.getElementById("statUnpaid").textContent = stats.unpaid;
}

function renderOrders() {
    const tbody = document.getElementById("ordersTbody");
    if (!tbody) return;
    const filterStatus = document.getElementById("orderStatusFilter")?.value || "";
    const filterText = document.getElementById("orderSearch")?.value.toLowerCase() || "";

    const filtered = allOrders.filter(o => {
        const matchStatus = filterStatus === "" || o.status === filterStatus;
        const matchText = filterText === "" ||
            o.id.toString().includes(filterText) ||
            o.customer.name.toLowerCase().includes(filterText) ||
            o.customer.email.toLowerCase().includes(filterText);
        return matchStatus && matchText;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center">Keine Bestellungen gefunden.</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(o => `
        <tr>
            <td>#${o.id}</td>
            <td>
                <strong>${escapeHtml(o.customer.name)}</strong><br>
                <small>${escapeHtml(o.customer.email)}</small>
            </td>
            <td>${new Date(o.created_at).toLocaleDateString()}</td>
            <td><span class="status-badge">${escapeHtml(o.status)}</span></td>
            <td>${escapeHtml(o.payment_status)}</td>
            <td><button class="button button-secondary" onclick="openOrder(${o.id})">Details</button></td>
        </tr>
    `).join("");
}

document.getElementById("orderSearch")?.addEventListener("input", renderOrders);
document.getElementById("orderStatusFilter")?.addEventListener("change", renderOrders);

async function openOrder(id) {
    const order = allOrders.find(o => o.id === id);
    if(!order) return;
    const modal = document.getElementById("orderModal");
    const body = document.getElementById("orderModalBody");

    body.innerHTML = `
        <div class="detail-section">
            <h3>Kunde</h3>
            <p><strong>Name:</strong> ${escapeHtml(order.customer.name)}</p>
            <p><strong>E-Mail:</strong> ${escapeHtml(order.customer.email)}</p>
            <button class="button button-secondary" onclick="openContactModal(${order.id})" style="margin-top:10px; font-size:12px">Kunden kontaktieren</button>
        </div>

        <div class="detail-section">
            <h3>Bestellung #${order.id}</h3>
            <p><strong>Datum:</strong> ${new Date(order.created_at).toLocaleString()}</p>

            <div style="margin-top: 15px; display: flex; gap: 15px;">
                <div>
                    <label><strong>Status:</strong></label><br>
                    <select class="admin-select" onchange="updateStatus(${order.id}, this.value)" style="margin-top:5px">
                        <option value="Eingegangen" ${order.status === 'Eingegangen' ? 'selected' : ''}>Eingegangen</option>
                        <option value="In Bearbeitung" ${order.status === 'In Bearbeitung' ? 'selected' : ''}>In Bearbeitung</option>
                        <option value="Bestellt" ${order.status === 'Bestellt' ? 'selected' : ''}>Bestellt</option>
                        <option value="Unterwegs" ${order.status === 'Unterwegs' ? 'selected' : ''}>Unterwegs</option>
                        <option value="Abgeschlossen" ${order.status === 'Abgeschlossen' ? 'selected' : ''}>Abgeschlossen</option>
                        <option value="Storniert" ${order.status === 'Storniert' ? 'selected' : ''}>Storniert</option>
                    </select>
                </div>
                <div>
                    <label><strong>Zahlungsstatus:</strong></label><br>
                    <select class="admin-select" onchange="updatePayment(${order.id}, this.value)" style="margin-top:5px">
                        <option value="offen" ${order.payment_status === 'offen' ? 'selected' : ''}>offen</option>
                        <option value="bezahlt" ${order.payment_status === 'bezahlt' ? 'selected' : ''}>bezahlt</option>
                    </select>
                </div>
            </div>
            <p style="margin-top:10px">Zahlungsart: ${escapeHtml(order.payment_method)}</p>
        </div>

        <div class="detail-section">
            <h3>Artikel</h3>
            ${order.items.map(i => `
                <div class="item-card">
                    <strong>${escapeHtml(i.product_name)}</strong>
                    ${i.size ? `<br><small>Größe: ${escapeHtml(i.size)}</small>` : ''}
                    ${i.color ? `<br><small>Farbe: ${escapeHtml(i.color)}</small>` : ''}
                    ${i.product_link ? `<br><a href="${escapeHtml(i.product_link)}" target="_blank" style="font-size:12px">Link öffnen</a>` : ''}
                    ${i.notes ? `<br><small>Notiz: ${escapeHtml(i.notes)}</small>` : ''}
                    <br><a href="${BASE_API}/orders/${order.id}/items/${i.id}/screenshot" target="_blank">
                        <img src="${BASE_API}/orders/${order.id}/items/${i.id}/screenshot" alt="Screenshot" onerror="this.style.display='none'">
                    </a>
                </div>
            `).join("")}
        </div>
    `;
    modal.hidden = false;
}


function closeModals() {
    document.getElementById("orderModal").hidden = true;
    const contactModal = document.getElementById("contactModal");
    if (!contactModal.hidden) {
        contactModal.hidden = true;
        document.getElementById("contactForm")?.reset();
        document.getElementById("contactMessageAlert").hidden = true;
    }
}

document.getElementById("closeOrderModal")?.addEventListener("click", closeModals);
document.getElementById("closeContactModal")?.addEventListener("click", closeModals);
document.getElementById("cancelContactModal")?.addEventListener("click", closeModals);

// Close on Escape
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModals();
});

// Close on Overlay Click
document.querySelectorAll(".modal-overlay").forEach(overlay => {
    overlay.addEventListener("click", (e) => {
        if (e.target === overlay) closeModals();
    });
});


async function updateStatus(id, newStatus) {
    try {
        await apiRequest(`/orders/${id}/status`, {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({status: newStatus})
        });
        await loadOrders();
    } catch (e) {
        alert(e.message);
    }
}

async function updatePayment(id, newStatus) {
    try {
        await apiRequest(`/orders/${id}/payment`, {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({payment_status: newStatus})
        });
        await loadOrders();
    } catch (e) {
        alert(e.message);
    }
}

function openContactModal(id) {
    document.getElementById("contactOrderId").value = id;
    document.getElementById("contactMessageAlert").hidden = true;
    document.getElementById("contactModal").hidden = false;
}


const contactForm = document.getElementById("contactForm");
if (contactForm) {
    contactForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = document.getElementById("contactOrderId").value;
        const subject = document.getElementById("contactSubject").value;
        const message = document.getElementById("contactMessage").value;
        const alertBox = document.getElementById("contactMessageAlert");
        const btn = e.target.querySelector("button[type='submit']");

        btn.disabled = true;
        btn.textContent = "Sende...";
        alertBox.hidden = true;
        try {
            await apiRequest(`/orders/${id}/contact`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({subject, message})
            });
            closeModals();
            alert("E-Mail wurde gesendet.");
        } catch (err) {
            alertBox.textContent = err.message;
            alertBox.hidden = false;
        } finally {
            btn.disabled = false;
            btn.textContent = "E-Mail senden";
        }
    });
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}
