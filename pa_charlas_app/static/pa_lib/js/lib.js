//TODO: traido de la app_semilla, unificar
/************************************************************************** */
//S: Util

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


function insertAtCursor(el_o_selector, textoAInsertar) { //U: inserta texto donde esta el cursor en una textArea
	const el_destino= typeof(el_o_selector)=="string" 
		? document.querySelector(el_o_selector) 
		: el_o_selector;
	//A: el_destino tiene un elemento
	
	if (document.selection) {	//A: es IE
		el_destino.focus();
		sel = document.selection.createRange();
		sel.text = textoAInsertar;
	}
	else if (el_destino.selectionStart || el_destino.selectionStart == '0') {//A: MOZILLA y otros
		var startPos = el_destino.selectionStart;
		var endPos = el_destino.selectionEnd;
		el_destino.value = el_destino.value.substring(0, startPos)
			+ textoAInsertar
			+ el_destino.value.substring(endPos, el_destino.value.length);

		el_destino.selectionStart= startPos+ textoAInsertar.length;
		el_destino.selectionEnd= el_destino.selectionStart;
	} 
	else {
		el_destino.value += textoAInsertar;
	}
	
	el_destino.focus(); //A: volver al elemento donde escribimos
}
/************************************************************************** */

//S: Autocompletar tags


Tags = []; //U: hashTags disponibles
TagsYUsuarios = []; //U: hashtags y usuarios disponibles

function traerTags(){
	$.ajax({
		type: 'GET',
		url:'/api/charla/', 
	})
	.done( recordarTags );
}

function recordarTags(hashtags){ //U: filtra lo que manda el servidor y lo carga en Tags
	for (let tag of hashtags) {  
		if ( ! tag.titulo.startsWith("#casual")) { //A: solo incluir los que no empiezan con casual
			Tags.push(tag.titulo);
		}
	};
};

function traerUsuarios(){
	$.ajax({
		type: 'GET',
		url:'/api/participante/', //TODO: de aca los queremos sacar o API mas especifica?
	}).done( recordarUsuarios );
}

function recordarUsuarios(usuarios) { 
	let users = [];
	for (let user of usuarios.results) {
		users.push('@'+user.username);
	}
	for(var i = users.length -1; i >=0; i--) { 
		//TODO: que hace este codigo? por que es necesario?
		if(users.indexOf(users[i]) !== i) users.splice(i,1);
  }
	TagsYUsuarios = Tags.concat(users);
	//DBG: console.log(TagsYUsuarios);
}



//Autocompletar#############################

function filterSubstring(Arr, Input) {
	return Arr.filter(e =>e.toLowerCase().includes(Input.toLowerCase()));
}

function htmlList(list, texto_dst) {
	var res = '';
	list.forEach( valor => {
		res += `<button type="button" onclick="insertaTag(this,'${texto_dst}')" value="${ valor }" class="btn btn-success mr-1">${ valor }</button>`; //TODO: dejarle el estilo del boton al que llama
	});
	return res;
}

function getMatchingTags(pattern) {
	if(!pattern){ return []; } //A: No hay nada para buscar
	return filterSubstring(TagsYUsuarios,pattern);
}

function insertaTag(valor, texto_dst) {
	insertAtCursor(texto_dst, valor.value);
}
    
function showTagButtons(pattern, tags_dst, texto_dst) { //U: para conectar con onKeyUp de un input, y pasarle el selector de la div donde aparecen los tags, y el textarea donde insertarlos
	var result = document.querySelector(tags_dst || '.result');
	let matching = getMatchingTags(pattern);
	result.innerHTML = htmlList(matching, texto_dst);
} 

traerTags();
traerUsuarios();
