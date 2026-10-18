function mudarVisibilidade(elementoQueChamou, idImagem){
    let imagem = document.getElementById(idImagem);

    if (imagem.style.visibility === "visible"){
        imagem.style.visibility = "hidden";
        elementoQueChamou.innerHTML = "Mostrar";
    }
    else{
        imagem.style.visibility = "visible";
        elementoQueChamou.innerHTML = "Esconder";
    }
}