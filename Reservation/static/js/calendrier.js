document.addEventListener('DOMContentLoaded', function() {
    const weekSelector = document.getElementById('weekSelector');
    const daysHeader = document.getElementById('daysHeader');
    const timeSlotsTable = document.getElementById('timeSlotsTable');
    const selectedSlotInput = document.getElementById('selectedSlot');
    
    let selectedSlot = null;

    // 1) Déterminer le "lundi" de la semaine en cours
    function getMondayOfCurrentWeek() {
        const currentDate = new Date();
        // getDay() renvoie 0 (dim) à 6 (sam)
        // On veut que 1 (lundi) soit la base
        let currentDay = currentDate.getDay();
        if (currentDay === 0) {
            // si on est dimanche, on met currentDay=7
            currentDay = 7;
        }
        // Soustraire (currentDay - 1) jours pour se mettre au lundi
        currentDate.setDate(currentDate.getDate() - (currentDay - 1));
        // now currentDate est le lundi de cette semaine
        return currentDate; 
    }

    function generateWeekOptions() {
        // lundi de la semaine courante
        const monday = getMondayOfCurrentWeek();

        // Nombre de semaines à générer (modifiez si besoin)
        const numberOfWeeks = 4;  

        // On crée dans le select <option>…</option> pour les 6 semaines suivantes
        for (let i = 0; i < numberOfWeeks; i++) {
            // On crée un nouveau date "startOfWeek" = (monday + i*7 jours)
            const startOfWeek = new Date(monday);
            startOfWeek.setDate(startOfWeek.getDate() + i * 7);

            // fin de semaine = startOfWeek + 4 jours (jusqu'au vendredi)
            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(endOfWeek.getDate() + 4);

            // format d'affichage
            const startStr = `${startOfWeek.getDate()} ${startOfWeek.toLocaleString('default', { month: 'short' })} ${startOfWeek.getFullYear()}`;
            const endStr = `${endOfWeek.getDate()} ${endOfWeek.toLocaleString('default', { month: 'short' })} ${endOfWeek.getFullYear()}`;

            // on crée l'élément <option>
            const option = document.createElement('option');
            // La valeur (value) = date ISO du lundi
            option.value = startOfWeek.toISOString().split('T')[0];
            // Le texte visible = "30 jan. 2025 - 3 févr. 2025" par ex.
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

    function generateTimeSlots(weekStart) {
        timeSlotsTable.innerHTML = '';
        const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];

        for (let hour = 9; hour <= 17; hour++) {
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

                // Au clic, on sélectionne le créneau
                slotCell.addEventListener('click', function() {
                    if (selectedSlot) {
                        selectedSlot.classList.remove('selected');
                    }
                    selectedSlot = slotCell;
                    slotCell.classList.add('selected');
                    // On met la valeur dans le champ caché
                    selectedSlotInput.value = slotCell.getAttribute('data-date') + " " + slotCell.getAttribute('data-time');
                    
                    // On active le bouton
                     validateBtn.disabled = false;
                });

                row.appendChild(slotCell);
            });
            timeSlotsTable.appendChild(row);
        }
    }

    // 2) Générer les <option> du sélecteur de semaines
    generateWeekOptions();

    // 3) Réagir quand l'utilisateur change la semaine
    weekSelector.addEventListener('change', function() {
        const selectedWeekStart = new Date(weekSelector.value); // valeur = "2025-01-30" par ex.
        generateDaysHeader(selectedWeekStart);
        generateTimeSlots(selectedWeekStart);

        // On réinitialise la sélection, donc on désactive le bouton
        selectedSlot = null;
        selectedSlotInput.value = '';
        validateBtn.disabled = true;
    });

    // 4) Déclencher immédiatement le "change"
    weekSelector.dispatchEvent(new Event('change'));

})

function goToProfilePage(numeroEtudiant) {
    window.location.href = "/profilEtudiant/" + numeroEtudiant + "/"; // Rediriger vers la page du profil de l'étudiant
}
;
