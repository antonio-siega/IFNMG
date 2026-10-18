let agora = new Date();

let tempo = {
    hora: agora.getHours(),
    minuto: agora.getMinutes(),
    segundo: agora.getSeconds()
};

let relogio = document.getElementById("relogio");

/* LÓGICA DE INCREMENTAÇÃO DE TEMPO */

function updateTime(){
    if (tempo.segundo<59) tempo.segundo++;       //se t != 59, incrementa. se não, reseta e tenta
    else {                                       //incrementar o valor superior. mesma lógica pro resto.
        tempo.segundo = 0;
        if (tempo.minuto<59) tempo.minuto++;
        else {
            tempo.minuto = 0;
            if (tempo.hora<23) tempo.hora++;
            else {
                tempo.hora = 0;
            }
        }
    }

    //utilizando padStart pra que valores de dígito único fiquem no formato correto
    let hora = String(tempo.hora).padStart(2,'0');
    let minuto = String(tempo.minuto).padStart(2,'0');
    let segundo = String(tempo.segundo).padStart(2,'0');

    relogio.innerHTML = `${hora}:${minuto}:${segundo}`;
}

/* também seria possível fazer isso só chamando Date() de novo e mudando o HTML a cada
   setInterval, mas acredito que essa não era a proposta do exercício. */

window.onload = updateTime();
setInterval(updateTime, 1000);