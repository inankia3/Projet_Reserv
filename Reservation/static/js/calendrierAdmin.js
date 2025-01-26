document.addEventListener('DOMContentLoaded', function() {
    const weekSelector = document.getElementById('weekSelector');
    const daysHeader = document.getElementById('daysHeader');
    const timeSlotsTable = document.getElementById('timeSlotsTable');
    const selectedHoursInput = document.getElementById('selectedHours');
    const blockButton = document.getElementById('blockButton');

    // Champ caché pour savoir si on bloque box1, box2, ou both
    const whichBoxInput = document.createElement('input');
    whichBoxInput.type = "hidden";
    whichBoxInput.name = "which_box";
    document.getElementById('adminCalendarForm').appendChild(whichBoxInput);

    // Ensemble des créneaux sélectionnés (ex: ["2025-02-10 09:00", "2025-02-10 10:00", ...])
    let selectedSlots = new Set();

    // 1) Générer la liste des semaines dans le select
    //    Si on est samedi/dimanche, on part sur le lundi de la semaine PROCHAINE.
    function generateWeekOptions() {
        const now = new Date();
        let currentDay = now.getDay(); // 0=Dim,1=Lun,...6=Sam

        if (currentDay === 0 || currentDay === 6) {
            // Dimanche (0) ou Samedi (6)
            // on avance jusqu'au lundi suivant
            const daysToNextMonday = 1 - currentDay; 
            now.setDate(now.getDate() + daysToNextMonday);
        } else {
            // On se ramène au lundi de la semaine courante
            const daysToMonday = (currentDay + 6) % 7; 
            now.setDate(now.getDate() - daysToMonday);
        }

        // On génère 5 semaines à partir de ce lundi (vous pouvez ajuster)
        for (let i = 0; i < 5; i++) {
            const startOfWeek = new Date(now);
            startOfWeek.setDate(startOfWeek.getDate() + i*7);
            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(endOfWeek.getDate() + 4); // Vendredi

            const option = document.createElement('option');
            option.value = startOfWeek.toISOString().split('T')[0];
            option.textContent = 
              `Semaine du ${startOfWeek.toLocaleDateString()} au ${endOfWeek.toLocaleDateString()}`;
            weekSelector.appendChild(option);
        }
    }

    // 2) Générer l'entête (lundi..vendredi)
    function generateDaysHeader(weekStart) {
        daysHeader.innerHTML = '';
        const days = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi'];
        for (let i=0; i<days.length; i++) {
            const th = document.createElement('th');
            const d = new Date(weekStart);
            d.setDate(d.getDate() + i);
            th.textContent = 
              `${days[i]} ${d.getDate()}/${d.getMonth()+1}/${d.getFullYear()}`;
            daysHeader.appendChild(th);
        }
    }

    // 3) Générer le tableau 9h->16h sur 5 colonnes (lundi..vendredi)
    //    + marquer bloqué/past si besoin
    function generateTimeSlots(weekStart) {
        timeSlotsTable.innerHTML = '';
        const days = 5; // Lundi..Vendredi
        for (let hour=9; hour<=16; hour++) {
            const row = document.createElement('tr');
            for (let dayIndex=0; dayIndex<days; dayIndex++) {
                const slotCell = document.createElement('td');
                slotCell.classList.add('time-slot');

                // Calcul de la date correspondante
                const currentDate = new Date(weekStart);
                currentDate.setDate(currentDate.getDate() + dayIndex);
                currentDate.setHours(hour,0,0,0);

                // On formate "YYYY-MM-DD HH:00"
                const isoDate = currentDate.toISOString().split('T')[0];
                const hourStr = `${hour}:00`;
                slotCell.setAttribute('data-date', isoDate);
                slotCell.setAttribute('data-hour', hourStr);

                // Affichage
                slotCell.textContent = hourStr;

                // Est-ce passé ?
                const now = new Date();
                if (currentDate < now) {
                    slotCell.classList.add('past');
                } else {
                    // TODO : si c'est déjà bloqué => check BDD (blockedSlots ?)
                    // ex: if (blockedSlots.includes( isoDate + " " + hourStr )) {
                    //     slotCell.classList.add('blocked');
                    // }

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

    // 4) Met à jour le champ caché
    function updateSelectedSlots() {
        const arr = Array.from(selectedSlots);
        selectedHoursInput.value = arr.join(',');
    }

    // 5) Sur le bouton "Bloquer" : on sélectionne box1, box2 ou both
    blockButton.addEventListener('click', function(e) {
        if (selectedSlots.size === 0) {
            alert("Aucun créneau sélectionné");
            e.preventDefault(); 
            return;
        }

        // Pop-up pour demander quel box bloquer
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
            whichBoxValue = "Les deux"; 
            // ou "both" => c'est vous qui décidez
        } else {
            alert("Réponse invalide. Veuillez réessayer.");
            e.preventDefault();
            return;
        }
        whichBoxInput.value = whichBoxValue;
        // Le formulaire se soumettra avec selected_hours + which_box
    });

    // 6) Lorsqu’on change la semaine
    weekSelector.addEventListener('change', function() {
        selectedSlots.clear();
        updateSelectedSlots();
        
        const mondayValue = weekSelector.value; // ex "2025-02-10"
        const mondayDate = new Date(mondayValue + "T00:00:00");
        generateDaysHeader(mondayDate);
        generateTimeSlots(mondayDate);
    });

    // Initialisation
    generateWeekOptions();
    weekSelector.dispatchEvent(new Event('change'));
});
