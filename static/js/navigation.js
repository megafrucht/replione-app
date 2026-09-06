document.addEventListener(
    "DOMContentLoaded",
    () => {
        const menuButton =
            document.querySelector(
                "[data-menu-toggle]"
            );
        const sideMenu =
            document.querySelector(
                "[data-side-menu]"
            );
        const overlay =
            document.querySelector(
                "[data-menu-overlay]"
            );
        if (!menuButton || !sideMenu) {
            return;
        }
        function openMenu() {
            sideMenu.classList.add("open"); sideMenu.classList.add("active");
            overlay?.classList.add("open"); overlay?.classList.add("active");
            document.body.classList.add("menu-open");
            menuButton.setAttribute(
                "aria-expanded",
                "true"
            );
        }
        function closeMenu() {
            sideMenu.classList.remove("open"); sideMenu.classList.remove("active");
            overlay?.classList.remove("open"); overlay?.classList.remove("active");
            document.body.classList.remove("menu-open");
            menuButton.setAttribute(
                "aria-expanded",
                "false"
            );
        }
        menuButton.addEventListener(
            "click",
            () => {
                if (
                    sideMenu.classList.contains("open")
                ) {
                    closeMenu();
                } else {
                    openMenu();
                }
            }
        );
        const closeButton = document.querySelector(".mobile-menu-close");
        if (closeButton) {
            closeButton.addEventListener("click", closeMenu);
        }
        overlay?.addEventListener(
            "click",
            closeMenu
        );
        sideMenu
            .querySelectorAll("a")
            .forEach((link) => {
                link.addEventListener(
                    "click",
                    closeMenu
                );
            });
        document.addEventListener(
            "keydown",
            (event) => {
                if (event.key === "Escape") {
                    closeMenu();
                }
            }
        );
    }
);
