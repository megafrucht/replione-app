document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("orderForm");

    if (!form) {
        return;
    }


    const screenshotInput =
        document.getElementById("productScreenshot");

    const imagePreview =
        document.getElementById("imagePreview");

    const previewImage =
        document.getElementById("previewImage");

    const previewFileName =
        document.getElementById("previewFileName");


    screenshotInput.addEventListener("change", () => {

        const file = screenshotInput.files[0];

        if (!file) {

            imagePreview.hidden = true;

            return;
        }


        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];


        if (!allowedTypes.includes(file.type)) {

            alert(
                "Bitte wähle eine JPG-, PNG- oder WEBP-Datei aus."
            );

            screenshotInput.value = "";

            imagePreview.hidden = true;

            return;
        }


        const reader = new FileReader();


        reader.onload = (event) => {

            previewImage.src = event.target.result;

            previewFileName.textContent = file.name;

            imagePreview.hidden = false;

        };


        reader.readAsDataURL(file);

    });


    form.addEventListener("submit", (event) => {

        event.preventDefault();


        const name =
            document.getElementById("productName").value.trim();

        const link =
            document.getElementById("productLink").value.trim();

        const size =
            document.getElementById("productSize").value.trim();

        const color =
            document.getElementById("productColor").value.trim();

        const notes =
            document.getElementById("productNotes").value.trim();

        const file =
            screenshotInput.files[0];


        if (!name) {

            alert(
                "Bitte gib deinem Produkt einen Namen."
            );

            return;
        }


        if (!file) {

            alert(
                "Bitte lade einen Screenshot des Produkts hoch."
            );

            return;
        }


        const reader = new FileReader();


        reader.onload = (event) => {

            const cart =
                window.replioneCart.getCart();


            cart.push({

                id:
                    Date.now().toString(),

                name,

                link,

                size,

                color,

                notes,

                image:
                    event.target.result

            });


            window.replioneCart.saveCart(cart);

            window.replioneCart.updateCartBadges();


            window.location.href =
                "warenkorb.html";

        };


        reader.readAsDataURL(file);

    });

});
