const API = "/api";
async function apiRequest(url, options = {}) {
    const response = await fetch(`${API}${url}`, {
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
            data?.detail || "Ein Fehler ist aufgetreten."
        );
    }
    return data;
}
async function getCurrentUser() {
    try {
        return await apiRequest("/auth/me");
    } catch {
        return {
            authenticated: false,
            user: null,
            is_admin: false,
        };
    }
}
async function logout() {
    try {
        await apiRequest("/auth/logout", {
            method: "POST",
        });
    } finally {
        window.location.href = "/";
    }
}
function showAuthMessage(message, type = "error") {
    const element =
        document.querySelector("[data-auth-message]");
    if (!element) {
        alert(message);
        return;
    }
    element.textContent = message;
    element.dataset.type = type;
    element.hidden = false;
}
async function handleLogin(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const email =
        form.querySelector('[name="email"]')?.value.trim();
    const password =
        form.querySelector('[name="password"]')?.value;
    if (!email || !password) {
        showAuthMessage(
            "Bitte E-Mail und Passwort eingeben."
        );
        return;
    }
    try {
        await apiRequest("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email,
                password,
            }),
        });
        window.location.href = "account.html";
    } catch (error) {
        showAuthMessage(error.message);
    }
}
async function handleRegister(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const name =
        form.querySelector('[name="name"]')?.value.trim();
    const email =
        form.querySelector('[name="email"]')?.value.trim();
    const password =
        form.querySelector('[name="password"]')?.value;
    if (!name || !email || !password) {
        showAuthMessage(
            "Bitte alle Pflichtfelder ausfüllen."
        );
        return;
    }
    try {
        await apiRequest("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name,
                email,
                password,
            }),
        });
        window.location.href = "account.html";
    } catch (error) {
        showAuthMessage(error.message);
    }
}
document.addEventListener("DOMContentLoaded", () => {
    const loginForm =
        document.querySelector(
            '[data-auth-form="login"]'
        );
    const registerForm =
        document.querySelector(
            '[data-auth-form="register"]'
        );
    loginForm?.addEventListener(
        "submit",
        handleLogin
    );
    registerForm?.addEventListener(
        "submit",
        handleRegister
    );
    document
        .querySelectorAll("[data-logout]")
        .forEach((button) => {
            button.addEventListener(
                "click",
                logout
            );
        });
});

// UI logic adjustments
document.addEventListener("DOMContentLoaded", () => {
    const switchButton = document.getElementById("authSwitchButton");
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const authTitle = document.getElementById("authTitle");
    const authSubtitle = document.getElementById("authSubtitle");
    const switchText = document.getElementById("authSwitchText");

    let registerMode = false;

    if (switchButton) {
        switchButton.addEventListener("click", () => {
            if (!loginForm || !registerForm) return;

            registerMode = !registerMode;

            loginForm.hidden = registerMode;
            registerForm.hidden = !registerMode;

            if (registerMode) {
                if (authTitle) authTitle.textContent = "Konto erstellen";
                if (authSubtitle) authSubtitle.textContent = "Erstelle dein persönliches Replione-Konto.";
                if (switchText) switchText.textContent = "Bereits ein Konto?";
                if (switchButton) switchButton.textContent = "Anmelden";
            } else {
                if (authTitle) authTitle.textContent = "Willkommen zurück";
                if (authSubtitle) authSubtitle.textContent = "Melde dich an, um deine Bestellungen zu verwalten.";
                if (switchText) switchText.textContent = "Noch kein Konto?";
                if (switchButton) switchButton.textContent = "Konto erstellen";
            }
        });
    }
});
