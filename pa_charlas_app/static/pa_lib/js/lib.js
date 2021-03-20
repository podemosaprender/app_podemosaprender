//TODO: traido de la app_semilla, unificar
/************************************************************************** */
//S: Util

$.ajax({
    type: 'GET',
    url:'https://si.podemosaprender.org/api/charla/', 
}).done(function(datos){
    listarHashtags(datos);
});

//Variables########################
var miArray = [];

CopyToClipboardEl= null; //U: el elemento donde ponemos texto para copiar
function copyToClipboard(texto) { //U: pone texto en el clipboard
	if (CopyToClipboardEl==null) {
		CopyToClipboardEl= document.createElement("textarea");   	
		CopyToClipboardEl.style.height="0px"; 
		CopyToClipboardEl.style.position= "fixed"; 
		CopyToClipboardEl.style.bottom= "0"; 
		CopyToClipboardEl.style.left= "0"; 
		document.body.append(CopyToClipboardEl);
	}
	CopyToClipboardEl.value= texto;	
	CopyToClipboardEl.textContent= texto;	
	CopyToClipboardEl.select();
	console.log("COPY "+document.execCommand('copy')); 
	document.getSelection().removeAllRanges();
}

function copyToClipboardEl(selector, permalink, ev) {
	var txt= document.querySelector(selector).innerText
	//DBG: console.log(ev)
	permalink= permalink || location.href;
	copyToClipboard('De '+permalink+'\n'+txt)
	if (ev) { ev.preventDefault(); } //A: no navegar
	return false; //A: no navegar
}

function listarTags(valor){
	textArea =  document.querySelector('#id_texto');
	textArea.insertAdjacentHTML("afterBegin", valor.text + ' ');
}

function listarHashtags(data){

	let hashtag = "";
	let casual = "casual";
    hashtags = data;

	for (let tag of hashtags) {  
		hashtag = tag.titulo.substr(1,6);

		if (hashtag !== casual) {
			miArray.push(tag.titulo);
		}
	};
};

function mostrarTags(){
	menu = document.querySelector(".hashtags");

	for (let el of miArray){
		menu.innerHTML += '<a class="dropdown-item" onclick="listarTags(this)" data-value= \"' + el + '\"> ' + el + '</a>'
	}
  };