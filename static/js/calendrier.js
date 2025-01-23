/* calendrier.js - Gère l'affichage et la sélection des créneaux horaires */

document.addEventListener('DOMContentLoaded', function() {
    const weekSelector = document.getElementById('weekSelector');
    const daysHeader = document.getElementById('daysHeader');
    const timeSlotsTable = document.getElementById('timeSlotsTable');
    const selectedSlotInput = document.getElementById('selectedSlot');
    let selectedSlot = null;

    // Fonction pour aller au profil étudiant
    // On ne la met pas forcément ici si on veut qu'elle soit accessible
    // globalement (ex. depuis le bouton onclick="goToProfilePage()"). Mais on peut :
    window.goToProfilePage = function(studentNumber) {
        if (!studentNumber) {
            alert("Aucun numéro étudiant trouvé. Impossible d'accéder au profil.");
            return;
        }
        window.location.href = "/profilEtudiant/" + studentNumber + "/";
    };

    // Génération dynamique des options de semaine
    function generateWeekOptions() {
        const currentDate = new Date();
        // Calcule l'écart pour arriver au lundi de la semaine courante
        const currentDay = currentDate.getDay(); // 0=Dimanche, 1=Lundi...
        const daysUntilMonday = (currentDay + 6) % 7;
        currentDate.setDate(currentDate.getDate() - daysUntilMonday);

        // On génère 6 semaines à partir de cette semaine
        for (let i = 0; i < 6; i++) {
            const option = document.createElement('option');
            const startOfWeek = new Date(currentDate);
            startOfWeek.setDate(startOfWeek.getDate() + i * 7);

            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(endOfWeek.getDate() + 4); // Jusqu'à vendredi

            const startStr = `${startOfWeek.getDate()} ${startOfWeek.toLocaleString('default', { month: 'short' })} ${startOfWeek.getFullYear()}`;
            const endStr = `${endOfWeek.getDate()} ${endOfWeek.toLocaleString('default', { month: 'short' })} ${endOfWeek.getFullYear()}`;

            option.value = startOfWeek.toISOString().split('T')[0];
            option.textContent = `${startStr} - ${endStr}`;
            weekSelector.appendChild(option);
        }
    }

    // Générer les en-têtes de jours (lundi à vendredi)
    function generateDaysHeader(weekStart) {
        daysHeader.innerHTML = '';
        const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];
        for (let i = 0; i < days.length; i++) {
            const th = document.createElement('th');
            const currentDate = new Date(weekStart);
            currentDate.setDate(currentDate.getDate() + i);

            // exemple : "Lundi 23 janvier"
            const dateStr = `${days[i]} ${currentDate.getDate()} ${currentDate.toLocaleString('default', { month: 'long' })}`;
            th.textContent = dateStr;
            daysHeader.appendChild(th);
        }
    }

    // Générer le tableau des créneaux (9h à 17h, du lundi au vendredi)
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

                // Affichage : "9:00", "10:00", etc.
                slotCell.textContent = `${hour}:00`;

                // Gérer la sélection au clic
                slotCell.addEventListener('click', function() {
                    if (selectedSlot) {
                        selectedSlot.classList.remove('selected');
                    }
                    selectedSlot = slotCell;
                    slotCell.classList.add('selected');
                    
                    selectedSlotInput.value = slotCell.getAttribute('data-date')
                        + " " + slotCell.getAttribute('data-time');
                });

                row.appendChild(slotCell);
            });
            timeSlotsTable.appendChild(row);
        }
    }

    // 1) Générer les options de semaine
    generateWeekOptions();

    // 2) Gérer le changement de semaine
    weekSelector.addEventListener('change', function() {
        const selectedWeekStart = new Date(weekSelector.value);
        generateDaysHeader(selectedWeekStart);
        generateTimeSlots(selectedWeekStart);
    });

    // 3) Déclenche la génération de la première semaine
    weekSelector.dispatchEvent(new Event('change'));
});
