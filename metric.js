function showMetrics(id, event) {
    var infoDiv = document.getElementById(id);

    // Obtener el texto del elemento que activó la función
    var buttonText = event.target.innerText;
    var flechaShowElement = event.target.querySelector('.flecha_show');

    // Verificar si el div está visible o no
    if (infoDiv.style.maxHeight === '0px' || infoDiv.style.maxHeight === '') {
        infoDiv.style.display = 'block';
        infoDiv.style.maxHeight = infoDiv.scrollHeight + 'px';
        flechaShowElement.innerHTML = '&#11167;'
    } else {
        infoDiv.style.maxHeight = '0';
        infoDiv.style.display = 'none';
        flechaShowElement.innerHTML = '&#11166;'
    }

    // Imprimir el texto del elemento que activó la función
    console.log('Texto del elemento:', buttonText);

    // Evitar la propagación del evento para que no afecte otros elementos
    event.stopPropagation();
}

