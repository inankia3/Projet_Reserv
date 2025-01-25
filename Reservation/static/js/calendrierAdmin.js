document.addEventListener('DOMContentLoaded', function() {
    const weekSelector = document.getElementById('weekSelector');
    const daysHeader = document.getElementById('daysHeader');
    const timeSlotsTable = document.getElementById('timeSlotsTable');
    const selectedHoursInput = document.getElementById('selectedHours');
    const blockButton = document.getElementById('blockButton');
    const whichBoxInput = document.createElement('input');  // Champ caché
    whichBoxInput.type = "hidden";
    whichBoxInput.name = "which_box";
    document.getElementById('adminCalendarForm').appendChild(whichBoxInput);

    // Ensemble des créneaux sélectionnés (ex: ["2025-02-10 09:00", "2025-02-10 10:00", ...])
    let selectedSlots = new Set();

    // --- 1) Générer la liste des semaines dans le select
    function generateWeekOptions() {
        const now = new Date();
        const currentDay = now.getDay(); // 0=Dim,1=Lun,...6=Sam
        // On se ramène au lundi
        let daysToMonday = (currentDay + 6) % 7; 
        now.setDate(now.getDate() - daysToMonday);

        for (let i=0; i<5; i++) {
            // On va générer 5 semaines
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

    // --- 2) Générer l'entête (lundi..vendredi) + corps
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

    // --- 3) Générer le tableau 9h->17h sur 5 colonnes (lundi..vendredi)
    //        + marquer bloqué/past si besoin
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

                // On formate "YYYY-MM-DD HH:MM"
                const isoDate = currentDate.toISOString().split('T')[0];
                const hourStr = `${hour}:00`;
                slotCell.setAttribute('data-date', isoDate);
                slotCell.setAttribute('data-hour', hourStr);

                // Affichage
                slotCell.textContent = hourStr;

                // --- Contrôles : est-ce passé ? est-ce bloqué ?
                const now = new Date();
                if (currentDate < now) {
                    // Passé
                    slotCell.classList.add('past');
                } else {
                    // TODO : si c'est déjà bloqué (ex. si l'admin a déjà réservé => 
                    //        verif BDD? => so, on a besoin d'un JSON `blockedSlots`.
                    //        Pour l'exemple, on gère "simulate" ou on skip.
                    //        => On appelle un array "blockedSlots" ?

                    // ex: if blockedSlots.includes( isoDate + " " + hourStr ) { 
                    //    slotCell.classList.add('blocked');
                    // } else {
                    //    -> on rend selectable
                    // }
                    
                    slotCell.addEventListener('click', function() {
                        // Si déjà bloqué, on ignore
                        if (slotCell.classList.contains('blocked')) {
                            return;
                        }
                        // Toggle la sélection
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

    // --- 4) Met à jour le champ caché
    function updateSelectedSlots() {
        // On transforme selectedSlots en tableau
        const arr = Array.from(selectedSlots);
        selectedHoursInput.value = arr.join(',');
    }

    // --- 5) Sur le bouton "Bloquer"
    blockButton.addEventListener('click', function(e) {
        // Si rien n’est sélectionné
        if (selectedSlots.size === 0) {
            alert("Aucun créneau sélectionné");
            e.preventDefault(); // on empêche l’envoi du form
        } else {
            // Sinon on laisse le form s’envoyer
            // Le champ hidden "selectedHours" contient la liste
        }
    });

    // --- 6) Gestion du "weekSelector" (pour charger un autre lundi)
    weekSelector.addEventListener('change', function() {
        selectedSlots.clear();
        updateSelectedSlots();
        
        const mondayValue = weekSelector.value; // "2025-02-10"
        const mondayDate = new Date(mondayValue + "T00:00:00");
        generateDaysHeader(mondayDate);
        generateTimeSlots(mondayDate);
    });

    blockButton.addEventListener('click', function(e) {
        if (selectedSlots.size === 0) {
            alert("Aucun créneau sélectionné");
            e.preventDefault(); 
            return;
        }

        // On affiche un pop-up pour demander quel box
        // Ex: "Voulez-vous bloquer le box1, le box2, ou les 2 ? 
        //     Taper '1', '2' ou 'both'"

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
        } else {
            // Réponse invalide
            alert("Réponse invalide. Veuillez réessayer.");
            e.preventDefault();
            return;
        }

        // On place la valeur dans whichBoxInput
        whichBoxInput.value = whichBoxValue;

        // On laisse le form se soumettre
    });

    // Initialisation
    generateWeekOptions();
    // Simuler un "change" pour la première semaine
    weekSelector.dispatchEvent(new Event('change'));
});
