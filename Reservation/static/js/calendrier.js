document.addEventListener('DOMContentLoaded', function() {
    const weekSelector = document.getElementById('weekSelector');
    const daysHeader = document.getElementById('daysHeader');
    const timeSlotsTable = document.getElementById('timeSlotsTable');
    const selectedSlotInput = document.getElementById('selectedSlot');
    
    // Si vous avez un bouton "Valider" avec id="validateBtn"
    // assurez-vous de le récupérer ci-dessous
    const validateBtn = document.getElementById('validateBtn');
    
    let selectedSlot = null;

    // 1) Déterminer le lundi de référence.
    //    Si on est samedi (6) ou dimanche (0), on bascule sur le lundi suivant.
    function getMondayOfCurrentWeek() {
        const currentDate = new Date();
        let currentDay = currentDate.getDay();  // 0=Dim, 1=Lun,...,6=Sam

        if (currentDay === 6 || currentDay === 0) {
            // Samedi ou dimanche
            // on veut aller au lundi de la semaine PROCHAINE
            // samedi => day=6 => 8-6=2 => on avance de 2 jours
            // dimanche => day=0 => 8-0=8 => on avance de 8 jours
            const daysToNextMonday = 1 - currentDay; 
            currentDate.setDate(currentDate.getDate() + daysToNextMonday);
        } else {
            // Sinon, on se positionne sur le lundi de la semaine en cours
            if (currentDay === 0) {
                // cas dimanche, on met day=7 (mais on gère déjà plus haut, donc pas indispensable)
                currentDay = 7;
            }
            // Soustraire (currentDay - 1) pour se mettre au lundi
            currentDate.setDate(currentDate.getDate() - (currentDay - 1));
        }

        return currentDate; 
    }

    // Génère les options de semaine dans le select <weekSelector>
    function generateWeekOptions() {
        // lundi de référence
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

    // Génère l'en-tête des jours (lundi..vendredi)
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

    // Génère le tableau des créneaux (9h..16h) pour 5 jours
    function generateTimeSlots(weekStart) {
        timeSlotsTable.innerHTML = '';
        const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];

        for (let hour = 9; hour <= 16; hour++) {
            const row = document.createElement('tr');
            days.forEach((day, index) => {
                const slotCell = document.createElement('td');
                const currentDate = new Date(weekStart);
                currentDate.setDate(currentDate.getDate() + index);

                slotCell.classList.add('time-slot');
                slotCell.setAttribute('data-date', currentDate.toISOString().split('T')[0]);
                slotCell.setAttribute('data-time', `${hour}:00`);
                slotCell.setAttribute('data-day', day);
                slotCell.textContent = `${hour}:00`;

                // Au clic, on sélectionne
                slotCell.addEventListener('click', function() {
                    if (selectedSlot) {
                        selectedSlot.classList.remove('selected');
                    }
                    selectedSlot = slotCell;
                    slotCell.classList.add('selected');
                    selectedSlotInput.value = slotCell.getAttribute('data-date') + " " + slotCell.getAttribute('data-time');

                    // On active le bouton (si défini)
                    if (validateBtn) {
                        validateBtn.disabled = false;
                    }
                });

                row.appendChild(slotCell);
            });
            timeSlotsTable.appendChild(row);
        }
    }

    // 1) Génère les semaines
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

// Fonction pour aller au profil étudiant (si besoin)
function goToProfilePage(numeroEtudiant) {
    window.location.href = "/profilEtudiant/" + numeroEtudiant + "/";
}
