function showMetrics(id, event) {
    var infoDiv = document.getElementById(id);
    var buttonText = event.target.innerText;
    var flechaShowElement = event.target.querySelector('.flecha_show');
    if (infoDiv.style.maxHeight === '0px' || infoDiv.style.maxHeight === '') {
        infoDiv.style.display = 'block';
        infoDiv.style.maxHeight = infoDiv.scrollHeight + 'px';
        flechaShowElement.innerHTML = '&#11167;'
    } else {
        infoDiv.style.maxHeight = '0';
        infoDiv.style.display = 'none';
        flechaShowElement.innerHTML = '&#11166;'
    }
    console.log('Texto del elemento:', buttonText);
    event.stopPropagation();
}

