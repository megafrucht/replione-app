document.addEventListener("DOMContentLoaded", () => {

    const burgerButton = document.getElementById("burgerButton");
    const mobileMenu = document.getElementById("mobileMenu");
    const mobileMenuClose = document.getElementById("mobileMenuClose");
    const menuOverlay = document.getElementById("menuOverlay");

    if (!burgerButton || !mobileMenu) {
        return;
    }


    function openMenu() {
        mobileMenu.classList.add("open");

        if (menuOverlay) {
            menuOverlay.classList.add("active");
        }

        burgerButton.setAttribute("aria-expanded", "true");

        document.body.style.overflow = "hidden";
    }


    function closeMenu() {
        mobileMenu.classList.remove("open");

        if (menuOverlay) {
            menuOverlay.classList.remove("active");
        }

        burgerButton.setAttribute("aria-expanded", "false");

        document.body.style.overflow = "";
    }


    burgerButton.addEventListener("click", openMenu);


    if (mobileMenuClose) {
        mobileMenuClose.addEventListener("click", closeMenu);
    }


    if (menuOverlay) {
        menuOverlay.addEventListener("click", closeMenu);
    }


    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            closeMenu();
        }

    });

});
