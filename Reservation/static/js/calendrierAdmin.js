document.addEventListener('DOMContentLoaded', function() {
    const weekSelector = document.getElementById('weekSelector');
    const daysHeader = document.getElementById('daysHeader');
    const timeSlotsTable = document.getElementById('timeSlotsTable');
    const selectedHoursInput = document.getElementById('selectedHours');
    const blockButton = document.getElementById('blockButton');

    const whichBoxInput = document.createElement('input');
    whichBoxInput.type = "hidden";
    whichBoxInput.name = "which_box";
    document.getElementById('adminCalendarForm').appendChild(whichBoxInput);

    let selectedSlots = new Set();

    function generateWeekOptions() {
        const now = new Date();
        let currentDay = now.getDay(); // 0=Dim,1=Lun,...6=Sam

        if (currentDay === 0 || currentDay === 6) {
            const daysToNextMonday = 8 - currentDay;
            now.setDate(now.getDate() + daysToNextMonday);
        } else {
            const daysToMonday = (currentDay + 6) % 7;
            now.setDate(now.getDate() - daysToMonday);
        }

        for (let i = 0; i < 5; i++) {
            const startOfWeek = new Date(now);
            startOfWeek.setDate(startOfWeek.getDate() + i * 7);
            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(endOfWeek.getDate() + 4);

            const option = document.createElement('option');
            option.value = startOfWeek.toISOString().split('T')[0];
            option.textContent = `Semaine du ${startOfWeek.toLocaleDateString()} au ${endOfWeek.toLocaleDateString()}`;
            weekSelector.appendChild(option);
        }
    }

    function generateDaysHeader(weekStart) {
        daysHeader.innerHTML = '';
        const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];
        for (let i = 0; i < days.length; i++) {
            const th = document.createElement('th');
            const d = new Date(weekStart);
            d.setDate(d.getDate() + i);
            th.textContent = `${days[i]} ${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
            daysHeader.appendChild(th);
        }
    }

    async function checkIfAllSubSlotsAreBlocked(date, hour) {
        try {
            const response = await fetch(`/get_blocked_slots/?date=${date}&hour=${hour}`);
            const data = await response.json();
            return data.all_blocked;
        } catch (error) {
            console.error('Error fetching blocked slots:', error);
            return false;
        }
    }

    async function generateTimeSlots(weekStart) {
        timeSlotsTable.innerHTML = '';
        const days = 5; // Lundi..Vendredi
        for (let hour = 9; hour <= 16; hour++) {
            const row = document.createElement('tr');
            for (let dayIndex = 0; dayIndex < days; dayIndex++) {
                const slotCell = document.createElement('td');
                slotCell.classList.add('time-slot');

                const currentDate = new Date(weekStart);
                currentDate.setDate(currentDate.getDate() + dayIndex);
                currentDate.setHours(hour, 0, 0, 0);

                const isoDate = currentDate.toISOString().split('T')[0];
                const hourStr = `${hour}:00`;
                slotCell.setAttribute('data-date', isoDate);
                slotCell.setAttribute('data-hour', hourStr);

                slotCell.textContent = hourStr;

                // Vérifier si tous les sous-créneaux sont passés
                const now = new Date();
                const allPast = [0, 15, 30, 45].every(minute => {
                    const subSlotDateTime = new Date(currentDate);
                    subSlotDateTime.setMinutes(minute);
                    return subSlotDateTime < now;
                });

                // Vérifier si tous les sous-créneaux sont bloqués
                const allBlocked = await checkIfAllSubSlotsAreBlocked(isoDate, hourStr);

                if (allPast || allBlocked) {
                    slotCell.classList.add('past');
                    slotCell.style.pointerEvents = 'none'; // Désactiver les clics
                    slotCell.style.opacity = '0.5'; // Rendre le créneau plus clair
                }

                // Au clic, on sélectionne uniquement si le créneau n'est ni passé ni bloqué
                if (!slotCell.classList.contains('past')) {
                    slotCell.addEventListener('click', function() {
                        if (slotCell.classList.contains('blocked')) {
                            return;
                        }
                        const slotKey = isoDate + " " + hourStr;
                        if (selectedSlots.has(slotKey)) {
                            selectedSlots.delete(slotKey);
                            slotCell.classList.remove('selected');
                        } else {
                            selectedSlots.add(slotKey);
                            slotCell.classList.add('selected');
                        }
                        updateSelectedSlots();
                    });
                }

                row.appendChild(slotCell);
            }
            timeSlotsTable.appendChild(row);
        }
    }

    function updateSelectedSlots() {
        const arr = Array.from(selectedSlots);
        selectedHoursInput.value = arr.join(',');
    }

    blockButton.addEventListener('click', function(e) {
        if (selectedSlots.size === 0) {
            alert("Aucun créneau sélectionné");
            e.preventDefault();
            return;
        }

        const choice = prompt("Tapez '1' pour bloquer le box1, '2' pour le box2, ou 'both' pour les deux.");
        if (!choice) {
            e.preventDefault();
            return;
        }

        let whichBoxValue = "";
        if (choice.toLowerCase() === "1") {
            whichBoxValue = "1";
        } else if (choice.toLowerCase() === "2") {
            whichBoxValue = "2";
        } else if (choice.toLowerCase() === "both") {
            whichBoxValue = "both";
        } else {
            alert("Réponse invalide. Veuillez réessayer.");
            e.preventDefault();
            return;
        }
        whichBoxInput.value = whichBoxValue;
    });

    weekSelector.addEventListener('change', function() {
        selectedSlots.clear();
        updateSelectedSlots();

        const mondayValue = weekSelector.value;
        const mondayDate = new Date(mondayValue + "T00:00:00");
        generateDaysHeader(mondayDate);
        generateTimeSlots(mondayDate);
    });

    generateWeekOptions();
    weekSelector.dispatchEvent(new Event('change'));
});