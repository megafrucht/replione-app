// Central API Client
async function api(path, options = {}) {
    const isFormData = options.body instanceof FormData;

    const headers = {
        ...options.headers
    };

    if (!isFormData) {
        headers["Content-Type"] = "application/json";
    }

    // Always include credentials for cookies
    const fetchOptions = {
        credentials: "include",
        ...options,
        headers
    };

    try {
        const response = await fetch(path, fetchOptions);

        if (!response.ok) {
            let errorMessage = "Ein unbekannter Fehler ist aufgetreten.";
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                // If parsing JSON fails, just use the status text
                errorMessage = response.statusText || errorMessage;
            }
            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
}

// Toast Notification
function showToast(msg, type="info") {
    let t = document.getElementById("toast");
    if (!t) {
        t = document.createElement("div");
        t.id = "toast";
        t.className = "toast";
        document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.background = type === "error" ? "#ef4444" : type === "success" ? "#22c55e" : "#171717";
    t.classList.add("show");
    setTimeout(() => t.classList.remove("show"), 3000);
}
