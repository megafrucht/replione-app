document.addEventListener("DOMContentLoaded", () => {

    const container =
        document.getElementById("ordersList");

    if (!container) {
        return;
    }


    const demoOrders = [

        {
            id: "RP-2026-0001",
            date: "03.09.2026",
            product: "Schwarzer Hoodie",
            status: "In Bearbeitung",
            step: 1
        },

        {
            id: "RP-2026-0002",
            date: "29.08.2026",
            product: "Sneaker",
            status: "Unterwegs",
            step: 3
        }

    ];


    const steps = [
        "Eingegangen",
        "In Bearbeitung",
        "Bestellt",
        "Unterwegs",
        "Abgeschlossen"
    ];


    container.innerHTML =
        demoOrders.map((order) => {

            const progress =
                steps.map((step, index) => {

                    const active =
                        index <= order.step
                            ? "active"
                            : "";


                    return `
                        <div class="progress-step ${active}">

                            <div class="progress-step-line"></div>

                            <span>
                                ${step}
                            </span>

                        </div>
                    `;

                }).join("");


            return `
                <article class="order-card">

                    <div class="order-top">

                        <div>

                            <div class="order-number">
                                ${order.id}
                            </div>

                            <div class="order-date">
                                ${order.date}
                            </div>

                        </div>


                        <div class="order-status">
                            ${order.status}
                        </div>

                    </div>


                    <div class="order-product">

                        <div class="order-product-image">
                            📦
                        </div>

                        <div>

                            <strong>
                                ${order.product}
                            </strong>

                            <small>
                                Deine Produktbestellung
                            </small>

                        </div>

                    </div>


                    <div class="order-progress">

                        ${progress}

                    </div>

                </article>
            `;

        }).join("");

});
