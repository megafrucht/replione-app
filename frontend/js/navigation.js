function updateUI() {
    const navAccountMobileBtn = document.getElementById('navAccountMobile');

    if (navAccountMobileBtn) {
        if (currentUser) {
            navAccountMobileBtn.textContent = 'Konto';
            navAccountMobileBtn.classList.remove('button-yellow');
            navAccountMobileBtn.classList.add('account-button');
            navAccountMobileBtn.className = 'nav-button';
        } else {
            navAccountMobileBtn.textContent = 'Login';
            navAccountMobileBtn.className = 'button button-yellow login-btn';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Burger Menu Logic
    const burgerMenu = document.getElementById('burgerMenu');
    const navLinks = document.getElementById('navLinks');

    if (burgerMenu && navLinks) {
        burgerMenu.addEventListener('click', () => {
            navLinks.classList.toggle('nav-active');
            burgerMenu.classList.toggle('nav-active');
        });
    }

    // Coming soon logic
    checkComingSoon();
});

function checkComingSoon() {
    if (window.location.pathname.includes('/admin')) return;

    const bypassToken = localStorage.getItem('replione_bypass');
    if (bypassToken === '040926LITlit!€') {
        return;
    }

    const overlay = document.createElement('div');
    overlay.id = 'coming-soon-overlay';
    overlay.innerHTML = `
        <h1 class="bypass-trigger">Du bist wohl noch etwas zu früh!</h1>
        <p>Am 04.09.2026 erfährst du mehr!</p>
    `;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    let clickCount = 0;
    let clickTimer;

    const trigger = overlay.querySelector('.bypass-trigger');
    if(trigger) {
        trigger.addEventListener('click', () => {
            clickCount++;
            clearTimeout(clickTimer);

            if (clickCount >= 5) {
                const pwd = prompt("Passwort:");
                if (pwd === '040926LITlit!€') {
                    localStorage.setItem('replione_bypass', pwd);
                    overlay.remove();
                    document.body.style.overflow = '';
                }
                clickCount = 0;
            } else {
                clickTimer = setTimeout(() => {
                    clickCount = 0;
                }, 1000);
            }
        });
    }
}
