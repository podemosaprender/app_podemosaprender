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


Tags = []; //U: hashtags disponibles

function traerTags(){
	$.ajax({
		type: 'GET',
		url:'https://si.podemosaprender.org/api/charla/', 
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


//Autocompletar#############################



function filterSubstring(Arr, Input) {
	return Arr.filter(e =>e.toLowerCase().includes(Input.toLowerCase()));
}

function htmlList(list){
	var res = '<ul>';
	list.forEach(e=>{
	   res += '<li>'+e+'</li>';
	})
	res += '</ul>';
	return res;
}

function getMatchingTags(pattern){
    if(!pattern){ //A: No hay nada para buscar
    	return [];
    }
    return filterSubstring(Tags,pattern);
}
    
function showTagsButtons(pattern, dst){
	var result = document.querySelector(dst || '.result');
	let matching = getMatchingTags(pattern);
    result.innerHTML = htmlList(matching);
 }
 traerTags();