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

/************************************************************************** */
//S: Autocompletar tags


Tags = []; //U: hashTags disponibles
TagsYUsuarios = []; //U: hashtags y usuarios disponibles

function traerTags(){
	$.ajax({
		type: 'GET',
		url:'/api/charla/', 
	}).done(function(datos){
		filtrarTags(datos);
	});
}

function filtrarTags(hashtags){ //U: filtra lo que manda el servidor y lo carga en Tags
	for (let tag of hashtags) {  
		if ( ! tag.titulo.startsWith("#casual")) { //A: solo incluir los que no empiezan con casual
			Tags.push(tag.titulo);
		}
	};
};

function traerUsuarios(){
	$.ajax({
		type: 'GET',
		url:'/api/texto/', //TODO: de aca los queremos sacar o API mas especifica?
	}).done(function(datos){
		filtrarUsuarios(datos)
	});
}

function filtrarUsuarios(usuarios) { //TODO: "usuarios" tiene usuarios o textos?
	let users = [];
	for (let user of usuarios.results) {
		users.push('@'+user.de_quien.username);
	}
	for(var i = users.length -1; i >=0; i--){
		if(users.indexOf(users[i]) !== i) users.splice(i,1);
  }
	TagsYUsuarios = Tags.concat(users);
	//DBG: console.log(TagsYUsuarios);
}



//Autocompletar#############################

function filterSubstring(Arr, Input) {
	return Arr.filter(e =>e.toLowerCase().includes(Input.toLowerCase()));
}

function htmlList(list){
	var res = "";
	list.forEach(e=>{
	res += '<button type="button" onclick="insertaTag(this)" value= \"' + e + '\" class="btn btn-success mr-1">'+e+'</button>';
	})
	return res;
}

function getMatchingTags(pattern){
    if(!pattern){ //A: No hay nada para buscar
    	return [];
    }
    return filterSubstring(TagsYUsuarios,pattern);
}
    
function showTagsButtons(pattern, dst){
	var result = document.querySelector(dst || '.result');
	let matching = getMatchingTags(pattern);
	result.innerHTML = htmlList(matching);
} 

function insertaTag(valor){
	textArea =  document.querySelector('#id_texto');
	textArea.insertAdjacentHTML("afterBegin", valor.value + ' ');
}
traerTags();
traerUsuarios();
