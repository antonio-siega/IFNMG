let tarefas = [];

function addTarefa(idInput){
    let input = document.getElementById(idInput);
    let textoTarefa = input.value;
    tarefas.push(textoTarefa);
    input.value = "";
}

function displayTarefas(){
    let div = document.createElement("div");
    let lista = document.getElementById("listaTarefas");


    if (!lista){
        lista = document.createElement("ul");
        lista.id = "listaTarefas";
    }


    for (let i=0; i<tarefas.length; i++){
        let elementoTarefa = document.createElement("li");
        elementoTarefa.textContent = tarefas[i];
        lista.appendChild(elementoTarefa);
    }

    tarefas.length = 0;
    
    div.appendChild(lista);
    document.body.appendChild(div);
}