/* A ideia aqui é que, na minha implementação, ao invés de pegar a altura do elemento utilizando
* "elemento.style.height", que só funcionaria para elementos que têm um estilo diretamente associado
* a eles, eu utilizei "getComputedStyle(elemento).height", que pega o estilo que foi aplicado ao elemento,
* ou seja, busca a informação do estilo geral dele. Assim, ao invés de precisar escrever algo como
* <img blabla style="foo">, eu posso aplicar um estilo ao próprio seletor img do documento HTML sem me
* preocupar. Daí, surgem dois problemas: primeiro, "getComputedStyle(elemento).height" devolve um valor
* em px, independente da folha de estilo aplicar a altura em porcentagem, e, segundo, também devolve com
* o "px" ao final. As funções auxiliares tira_letras_simbolos e get_altura_porcento servem para transformar
* esses valores em valores utilizáveis em cálculos.
*/

function tira_letras_simbolos(string){ //Para remover "px", "%", "em", etc. do final de valores de estilo
    let numeros = [];

    for (let i = 0; i<10; i++){
        numeros.push(String(i)); //array com todos números decimais com tipo String
    }

    let aux = "";

    for (let i=0; i<string.length; i++){
        if (numeros.includes(string[i])) aux += string[i]; 
        else break; //quando chega no primeiro não-número, para.
    }

    return aux;
}

function get_altura_porcento(elemento){
    /* Para conseguir um valor em porcentagem a partir do valor em px, precisamos pegar a altura,
    dividir pela altura do elemento pai (também em px) e multiplicar por 100. O arredondamento
    é pelo fato de que operações com números de ponto flutuante dão resultados imprecisos.*/

    let alturaElemento = tira_letras_simbolos(getComputedStyle(elemento).height);
    let alturaElementoPai = tira_letras_simbolos(getComputedStyle(elemento.parentNode).height);

    let porcentagem = Math.round((alturaElemento/alturaElementoPai)*100);

    return porcentagem;
}

function mudaZoom(idImagem, variacao, tipo){ //"tipo" define se é zoom in ou zoom out. 1 = in, 0 = out.
                                             //"variacao" deve ser um valor em % (só o número) correspondente ao tanto
                                             //que deve ser aumentado ou diminuído na altura do elemento.
    let imagem = document.getElementById(idImagem);

    let alturas = {
        atual: get_altura_porcento(imagem),
        maxima: tira_letras_simbolos(getComputedStyle(imagem).maxHeight), //max e minHeight já vêm em % certinho
        minima: tira_letras_simbolos(getComputedStyle(imagem).minHeight)
    }

    if (tipo){
        if (alturas.atual < alturas.maxima){
            imagem.style.height = `${alturas.atual + variacao}%`;
        }
    }
    else {
        if (alturas.atual > alturas.minima){
            imagem.style.height = `${alturas.atual - variacao}%`
        }
    }
}