let currentUser = null;

async function loadCurrentUser() {
    try {
        currentUser = await api("/api/auth/me");
    } catch (e) {
        currentUser = null;
    }
    updateUI();
    if (typeof onUserLoaded === "function") {
        onUserLoaded();
    }
}

async function loginUser(email, password) {
    await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
    });
    await loadCurrentUser();
    if (typeof loadCart === "function") {
        await loadCart();
    }
}

async function registerUser(name, email, password) {
    await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password })
    });
    await loadCurrentUser();
}

async function logoutUser() {
    await api("/api/auth/logout", { method: "POST" });
    currentUser = null;
    if (typeof loadCart === "function") {
        await loadCart();
    }
    updateUI();
    window.location.href = "/";
}

document.addEventListener("DOMContentLoaded", () => {
    loadCurrentUser();
});
