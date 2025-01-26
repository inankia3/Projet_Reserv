function validateStudentNumber() {
    const inputEtud = document.getElementById('inputEtud').value;

    // Vérifier que le numéro étudiant est un nombre à 8 chiffres
    const regex = /^\d{8}$/;
    if (!regex.test(inputEtud)) {
        alert("Le numéro étudiant saisi n'est pas valide.");
        return false; // Empêcher la soumission du formulaire
    }

    return true; // Autoriser la soumission du formulaire
}