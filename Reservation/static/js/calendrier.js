document.addEventListener('DOMContentLoaded', function() {
    const weekSelector = document.getElementById('weekSelector');
    const daysHeader = document.getElementById('daysHeader');
    const timeSlotsTable = document.getElementById('timeSlotsTable');
    const selectedSlotInput = document.getElementById('selectedSlot');
    const validateBtn = document.getElementById('validateBtn');

    let selectedSlot = null;

    function getMondayOfCurrentWeek() {
        const currentDate = new Date();
        let currentDay = currentDate.getDay();  // 0=Dim, 1=Lun,...,6=Sam

        if (currentDay === 6 || currentDay === 0) {
            const daysToNextMonday = 8 - currentDay;
            currentDate.setDate(currentDate.getDate() + daysToNextMonday);
        } else {
            if (currentDay === 0) {
                currentDay = 7;
            }
            currentDate.setDate(currentDate.getDate() - (currentDay - 1));
        }

        return currentDate;
    }

    function generateWeekOptions() {
        const monday = getMondayOfCurrentWeek();
        const numberOfWeeks = 4;

        for (let i = 0; i < numberOfWeeks; i++) {
            const startOfWeek = new Date(monday);
            startOfWeek.setDate(startOfWeek.getDate() + i * 7);

            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(endOfWeek.getDate() + 4);

            const startStr = `${startOfWeek.getDate()} ${startOfWeek.toLocaleString('default', { month: 'short' })} ${startOfWeek.getFullYear()}`;
            const endStr = `${endOfWeek.getDate()} ${endOfWeek.toLocaleString('default', { month: 'short' })} ${endOfWeek.getFullYear()}`;

            const option = document.createElement('option');
            option.value = startOfWeek.toISOString().split('T')[0];
            option.textContent = `${startStr} - ${endStr}`;
            weekSelector.appendChild(option);
        }
    }

    function generateDaysHeader(weekStart) {
        daysHeader.innerHTML = '';
        const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];
        for (let i = 0; i < days.length; i++) {
            const th = document.createElement('th');
            const currentDate = new Date(weekStart);
            currentDate.setDate(currentDate.getDate() + i);
            const dateStr = `${days[i]} ${currentDate.getDate()} ${currentDate.toLocaleString('default', { month: 'long' })}`;
            th.textContent = dateStr;
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
        const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];

        for (let hour = 9; hour <= 16; hour++) {
            const row = document.createElement('tr');
            for (let dayIndex = 0; dayIndex < days.length; dayIndex++) {
                const slotCell = document.createElement('td');
                const currentDate = new Date(weekStart);
                currentDate.setDate(currentDate.getDate() + dayIndex);

                slotCell.classList.add('time-slot');
                slotCell.setAttribute('data-date', currentDate.toISOString().split('T')[0]);
                slotCell.setAttribute('data-time', `${hour}:00`);
                slotCell.setAttribute('data-day', days[dayIndex]);
                slotCell.textContent = `${hour}:00`;

                // Vérifier si tous les sous-créneaux sont passés
                const now = new Date();
                const slotDateTime = new Date(currentDate);
                slotDateTime.setHours(hour, 0, 0, 0);

                const allPast = [0, 15, 30, 45].every(minute => {
                    const subSlotDateTime = new Date(slotDateTime);
                    subSlotDateTime.setMinutes(minute);
                    return subSlotDateTime < now;
                });

                // Vérifier si tous les sous-créneaux sont bloqués
                const allBlocked = await checkIfAllSubSlotsAreBlocked(currentDate.toISOString().split('T')[0], `${hour}:00`);

                if (allPast || allBlocked) {
                    slotCell.classList.add('past');
                    slotCell.style.pointerEvents = 'none'; // Désactiver les clics
                    slotCell.style.opacity = '0.5'; // Rendre le créneau plus clair
                }

                // Au clic, on sélectionne uniquement si le créneau n'est ni passé ni bloqué
                if (!slotCell.classList.contains('past')) {
                    slotCell.addEventListener('click', function() {
                        if (selectedSlot) {
                            selectedSlot.classList.remove('selected');
                        }
                        selectedSlot = slotCell;
                        slotCell.classList.add('selected');
                        selectedSlotInput.value = slotCell.getAttribute('data-date') + " " + slotCell.getAttribute('data-time');

                        if (validateBtn) {
                            validateBtn.disabled = false;
                        }
                    });
                }

                row.appendChild(slotCell);
            }
            timeSlotsTable.appendChild(row);
        }
    }

    // 1) Générer les semaines
    generateWeekOptions();

    // 2) Lorsque l'utilisateur choisit une semaine
    weekSelector.addEventListener('change', function() {
        const selectedWeekStart = new Date(weekSelector.value);
        generateDaysHeader(selectedWeekStart);
        generateTimeSlots(selectedWeekStart);

        // On réinitialise la sélection
        selectedSlot = null;
        selectedSlotInput.value = '';
        if (validateBtn) {
            validateBtn.disabled = true;
        }
    });

    // 3) Déclenche immédiatement un "change" pour initialiser
    weekSelector.dispatchEvent(new Event('change'));
});

function goToProfilePage(studentNumber) {
    window.location.href = `/profilEtudiant/${studentNumber}/`;
}