document.addEventListener("DOMContentLoaded", () => {

    const loginForm =
        document.getElementById("loginForm");

    const registerForm =
        document.getElementById("registerForm");

    const switchButton =
        document.getElementById("authSwitchButton");

    const switchText =
        document.getElementById("authSwitchText");

    const authTitle =
        document.getElementById("authTitle");

    const authSubtitle =
        document.getElementById("authSubtitle");

    const authMessage =
        document.getElementById("authMessage");

    const logoutButton =
        document.getElementById("logoutButton");


    let registerMode = false;


    function showMessage(message) {

        if (!authMessage) {
            return;
        }

        authMessage.textContent = message;

        authMessage.hidden = false;

    }


    function updateAuthView() {

        if (!loginForm || !registerForm) {
            return;
        }


        registerMode = !registerMode;


        loginForm.hidden = registerMode;

        registerForm.hidden = !registerMode;


        if (registerMode) {

            authTitle.textContent =
                "Konto erstellen";

            authSubtitle.textContent =
                "Erstelle dein persönliches Replione-Konto.";

            switchText.textContent =
                "Bereits ein Konto?";

            switchButton.textContent =
                "Anmelden";

        } else {

            authTitle.textContent =
                "Willkommen zurück";

            authSubtitle.textContent =
                "Melde dich an, um deine Bestellungen zu verwalten.";

            switchText.textContent =
                "Noch kein Konto?";

            switchButton.textContent =
                "Konto erstellen";

        }

    }


    if (switchButton) {

        switchButton.addEventListener(
            "click",
            updateAuthView
        );

    }


    if (loginForm) {

        loginForm.addEventListener("submit", (event) => {

            event.preventDefault();


            const email =
                document.getElementById("loginEmail").value.trim();


            localStorage.setItem(
                "replione_demo_user",
                JSON.stringify({
                    name: "Demo Benutzer",
                    email
                })
            );


            showMessage(
                "Demo-Login erfolgreich. Das echte Login-System folgt mit dem Backend."
            );

        });

    }


    if (registerForm) {

        registerForm.addEventListener("submit", (event) => {

            event.preventDefault();


            const name =
                document.getElementById("registerName").value.trim();

            const email =
                document.getElementById("registerEmail").value.trim();


            localStorage.setItem(
                "replione_demo_user",
                JSON.stringify({
                    name,
                    email
                })
            );


            showMessage(
                "Demo-Konto erstellt. Das echte Konto-System folgt mit dem Backend."
            );

        });

    }


    if (logoutButton) {

        logoutButton.addEventListener("click", () => {

            localStorage.removeItem(
                "replione_demo_user"
            );

            window.location.href =
                "login.html";

        });

    }


    const accountName =
        document.getElementById("accountName");

    const accountEmail =
        document.getElementById("accountEmail");


    if (accountName || accountEmail) {

        try {

            const user =
                JSON.parse(
                    localStorage.getItem(
                        "replione_demo_user"
                    )
                );


            if (user) {

                if (accountName) {
                    accountName.textContent =
                        user.name;
                }

                if (accountEmail) {
                    accountEmail.textContent =
                        user.email;
                }

            }

        } catch {
            // Demo-Daten ignorieren
        }

    }

});
