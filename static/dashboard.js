// listens for click of Limpiar and wipes text in activities text area
document.addEventListener('DOMContentLoaded', function () {
    const clearButton = document.getElementById('clear-btn');   // green button
    const textarea = document.getElementById('activities-text-area');

    clearButton.addEventListener('click', function () {
        textarea.value = "";
    });
});


// updates dashboard regularly
function updateDashboard() {
        fetch('/data')
            .then(response => response.json())
            .then(data => {

                const topRightEl = document.getElementById('top-right');
                topRightEl.textContent = data.top_right.content;
                topRightEl.classList.remove('general-0', 'general-1','general-2','general-3');
                topRightEl.classList.add(`general-${data.top_right.status}`);

                document.getElementById('top-left').textContent = data.top_left;

                const iconMap = {
                    3: "bi-check-circle-fill text-success",
                    0: "bi-hourglass-split text-secondary",
                    2: "bi-x-circle-fill text-danger",
                    1: "bi-caret-right-square text-success"
                };

                const labelMap = {
                    1: "Active",
                    0: "Inactive",
                    2: "Crashed",
                    3: "Completed"
                };

                // Update first row of cards (0-11)
                for (let i = 0; i < 12; i++) {
                    const card = data.cards[i];
                    if (card) { // Ensure card data exists for this index
                        document.getElementById(`card-title-${i}`).textContent = card.title;

                        const progressEl = document.getElementById(`card-progress-${i}`);
                        progressEl.style.width = card.progress + '%';
                        progressEl.setAttribute('aria-valuenow', card.progress);
                        progressEl.textContent = card.progress + '%';

                        document.getElementById(`card-text-${i}`).textContent = card.text;
                        document.getElementById(`card-status-label-${i}`).textContent = card.lastUpdate;

                        const cardEl = document.getElementById(`card-${i}`);
                        cardEl.classList.remove('status-1', 'status-2', 'status-0', "status-3");
                        cardEl.classList.add(`status-${card.status}`);

                        const iconEl = document.getElementById(`card-icon-${i}`);
                        iconEl.className = `bi ${iconMap[card.status]}`;
                    }
                }

                // Update second row of cards (12-23)
                for (let i = 0; i < 12; i++) {
                    const card = data.cards[i + 12]; // Offset by 12 for the second row
                    if (card) { // Ensure card data exists for this index
                        document.getElementById(`card-title-${i + 12}`).textContent = card.title;

                        const progressEl = document.getElementById(`card-progress-${i + 12}`);
                        progressEl.style.width = card.progress + '%';
                        progressEl.setAttribute('aria-valuenow', card.progress);
                        progressEl.textContent = card.progress + '%';

                        document.getElementById(`card-text-${i + 12}`).textContent = card.text;
                        document.getElementById(`card-status-label-${i + 12}`).textContent = card.lastUpdate;

                        const cardEl = document.getElementById(`card-${i + 12}`);
                        cardEl.classList.remove('status-1', 'status-2', 'status-0', "status-3");
                        cardEl.classList.add(`status-${card.status}`);

                        const iconEl = document.getElementById(`card-icon-${i + 12}`);
                        iconEl.className = `bi ${iconMap[card.status]}`;
                    }
                }

                // Update KPIs and Activities Text Area
                const kpi_members = document.getElementById('kpi-members');
                kpi_members.innerHTML = '';  // Clear previous content
                const div1 = document.createElement('div');
                    div1.innerHTML = data.kpi_members;
                    kpi_members.appendChild(div1);

                const kpi_placas = document.getElementById('kpi-placas');
                kpi_placas.innerHTML = '';  // Clear previous content
                const div2 = document.createElement('div');
                    div2.innerHTML = data.kpi_placas;
                    kpi_placas.appendChild(div2);

                const kpi_truecaptcha_balance = document.getElementById('kpi-truecaptcha-balance');
                kpi_truecaptcha_balance.innerHTML = '';  // Clear previous content
                const div3 = document.createElement('div');
                    div3.innerHTML = data.kpi_truecaptcha_balance;
                kpi_truecaptcha_balance.appendChild(div3);

                const bottom_left = document.getElementById('activities-text-area');
                bottom_left.value = data.bottom_left.join('\n');
                
            });
    }

    setInterval(updateDashboard, 2500);
    updateDashboard();