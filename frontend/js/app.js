// Bootstrapper for modular JS
// Include these scripts in HTML in this order:
// 1. api.js
// 2. auth.js
// 3. cart.js
// 4. navigation.js
// 5. app.js (this file, for general page-specific logic)

async function onUserLoaded() {
    if (typeof loadCart === "function") {
        await loadCart();
    }
}
