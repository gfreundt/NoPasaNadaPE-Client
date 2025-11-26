// listens for click of Limpiar and wipes text in activities text area
document.addEventListener('DOMContentLoaded', function () {
    const clearButton = document.getElementById('clear-btn');
    const textarea = document.getElementById('activities-text-area');

    if (clearButton && textarea) {
        clearButton.addEventListener('click', function () {
            textarea.value = "";
        });
    }
});

// updates dashboard regularly
function updateDashboard() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            
            const iconMap = {
                3: "bi-check-circle-fill text-success",
                0: "bi-hourglass-split text-secondary",
                2: "bi-x-circle-fill text-danger",
                1: "bi-caret-right-square text-success"
            };

            // Update cards (0-31)
            // Range updated to 32 to match HTML
            for (let i = 0; i < 32; i++) {
                const card = data.cards[i];
                // Ensure card data exists for this index before trying to update
                if (card) {
                    const titleEl = document.getElementById(`card-title-${i}`);
                    if (titleEl) titleEl.textContent = card.title;

                    // Progress bar update logic removed

                    const textEl = document.getElementById(`card-text-${i}`);
                    if (textEl) textEl.textContent = card.text;

                    const statusLabelEl = document.getElementById(`card-status-label-${i}`);
                    if (statusLabelEl) statusLabelEl.textContent = card.lastUpdate;

                    const cardEl = document.getElementById(`card-${i}`);
                    if (cardEl) {
                        cardEl.classList.remove('status-1', 'status-2', 'status-0', "status-3");
                        cardEl.classList.add(`status-${card.status}`);
                    }

                    const iconEl = document.getElementById(`card-icon-${i}`);
                    if (iconEl) {
                        iconEl.className = `bi ${iconMap[card.status]}`;
                    }
                }
            }

            // Update KPIs
            // We check if the element exists before updating to prevent errors
            const kpi_placas = document.getElementById('kpi-active-threads');
            if (kpi_placas) {
                kpi_placas.innerHTML = '';
                const div = document.createElement('div');
                div.innerHTML = data.kpi_active_threads;
                kpi_placas.appendChild(div);
            }

            const kpi_truecaptcha_balance = document.getElementById('kpi-truecaptcha-balance');
            if (kpi_truecaptcha_balance) {
                kpi_truecaptcha_balance.innerHTML = '';
                const div = document.createElement('div');
                div.innerHTML = data.kpi_truecaptcha_balance;
                kpi_truecaptcha_balance.appendChild(div);
            }

            const kpi_zeptomail_balance = document.getElementById('kpi-zeptomail-balance');
            if (kpi_zeptomail_balance) {
                kpi_zeptomail_balance.innerHTML = '';
                const div = document.createElement('div');
                div.innerHTML = data.kpi_zeptomail_balance;
                kpi_zeptomail_balance.appendChild(div);
            }
            
            const kpi_twocaptcha_balance = document.getElementById('kpi-twocaptcha-balance');
            if (kpi_twocaptcha_balance) {
                kpi_twocaptcha_balance.innerHTML = '';
                const div = document.createElement('div');
                div.innerHTML = data.kpi_twocaptcha_balance;
                kpi_twocaptcha_balance.appendChild(div);
            }
            
            const kpi_brightdata_balance = document.getElementById('kpi-brightdata-balance');
            if (kpi_brightdata_balance) {
                kpi_brightdata_balance.innerHTML = '';
                const div = document.createElement('div');
                div.innerHTML = data.kpi_brightdata_balance;
                kpi_brightdata_balance.appendChild(div);
            }
            
            const kpi_googlecloud_balance = document.getElementById('kpi-googlecloud-balance');
            if (kpi_googlecloud_balance) {
                kpi_googlecloud_balance.innerHTML = '';
                const div = document.createElement('div');
                div.innerHTML = data.kpi_googlecloud_balance;
                kpi_googlecloud_balance.appendChild(div);
            }
            
            const kpi_cloudfare_balance = document.getElementById('kpi-cloudfare-balance');
            if (kpi_cloudfare_balance) {
                kpi_cloudfare_balance.innerHTML = '';
                const div = document.createElement('div');
                div.innerHTML = data.kpi_cloudfare_balance;
                kpi_cloudfare_balance.appendChild(div);
            }

            const bottom_left = document.getElementById('activities-text-area');
            if (bottom_left && data.bottom_left) {
                bottom_left.value = data.bottom_left.join('\n');
            }
            
        })
        .catch(error => console.error('Error updating dashboard:', error));
}

setInterval(updateDashboard, 2500);
updateDashboard();