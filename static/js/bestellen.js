const ORDER_API = "/api";
function showOrderMessage(
    message,
    type = "error"
) {
    const element =
        document.querySelector(
            "[data-order-message]"
        );
    if (!element) {
        alert(message);
        return;
    }
    element.textContent = message;
    element.dataset.type = type;
    element.hidden = false;
}
function validateScreenshot(file) {
    if (!file) {
        return "Bitte einen Screenshot auswählen.";
    }
    const allowed = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ];
    if (!allowed.includes(file.type)) {
        return "Bitte JPG, PNG oder WebP verwenden.";
    }
    if (file.size > 8 * 1024 * 1024) {
        return "Der Screenshot darf maximal 8 MB groß sein.";
    }
    return null;
}
function setupScreenshotPreview() {
    const input =
        document.querySelector(
            'input[type="file"][name="screenshot"]'
        );
    const preview =
        document.querySelector(
            "[data-screenshot-preview]"
        );
    if (!input) {
        return;
    }
    input.addEventListener(
        "change",
        () => {
            const file = input.files?.[0];
            if (!file) {
                if (preview) {
                    preview.hidden = true;
                    let img = preview.querySelector("img"); if(!img && preview.tagName.toLowerCase() === "img") { img = preview; }
                if (img) img.removeAttribute("src");
                }
                return;
            }
            const error =
                validateScreenshot(file);
            if (error) {
                input.value = "";
                if (preview) {
                    preview.hidden = true;
                }
                showOrderMessage(error);
                return;
            }
            if (preview) {
                let img = preview.querySelector("img"); if(!img && preview.tagName.toLowerCase() === "img") { img = preview; }
                if (img) img.src = URL.createObjectURL(file);
                preview.hidden = false;
            }
        }
    );
}
async function submitOrderItem(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const productName =
        form.querySelector(
            '[name="product_name"]'
        )?.value.trim();
    const screenshot =
        form.querySelector(
            '[name="screenshot"]'
        )?.files?.[0];
    if (!productName) {
        showOrderMessage(
            "Der Produktname ist erforderlich."
        );
        return;
    }
    const screenshotError =
        validateScreenshot(screenshot);
    if (screenshotError) {
        showOrderMessage(
            screenshotError
        );
        return;
    }
    const formData = new FormData();
    formData.append(
        "product_name",
        productName
    );
    formData.append(
        "screenshot",
        screenshot
    );
    const fields = [
        "product_link",
        "size",
        "color",
        "notes",
    ];
    fields.forEach((name) => {
        const input =
            form.querySelector(
                `[name="${name}"]`
            );
        if (input?.value.trim()) {
            formData.append(
                name,
                input.value.trim()
            );
        }
    });
    const button =
        form.querySelector(
            '[type="submit"]'
        );
    if (button) {
        button.disabled = true;
        button.textContent =
            "Wird hinzugefügt …";
    }
    try {
        const response =
            await fetch(
                `${ORDER_API}/cart/items`,
                {
                    method: "POST",
                    credentials: "include",
                    body: formData,
                }
            );
        let data = null;
        try {
            data = await response.json();
        } catch {}
        if (!response.ok) {
            throw new Error(
                data?.detail ||
                "Produkt konnte nicht hinzugefügt werden."
            );
        }
        window.location.href =
            "warenkorb.html";
    } catch (error) {
        showOrderMessage(
            error.message
        );
        if (button) {
            button.disabled = false;
            button.textContent =
                "In den Warenkorb";
        }
    }
}
document.addEventListener(
    "DOMContentLoaded",
    () => {
        setupScreenshotPreview();
        const form =
            document.querySelector(
                '[data-order-form]'
            );
        form?.addEventListener(
            "submit",
            submitOrderItem
        );
    }
);
