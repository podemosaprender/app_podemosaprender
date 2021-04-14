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


Tags = []; //U: hashTags disponibles sin casual
TagsTodos = []; 
TagsYUsuarios = []; //U: hashtags y usuarios disponibles
UsuariosPk = {};//U: usuarios con su pk disponibles

function traerTags(){
	return $.ajax({
		type: 'GET',
		url:'/api/charla/', 
	})
	.done( recordarTags );
}

function recordarTags(hashtags){ //U: filtra lo que manda el servidor y lo carga en Tags
	Tags= []; TagsTodos= []; //A: volver a inicializar, sino se van duplicando
	for (let tag of hashtags) {  
		if ( ! tag.titulo.startsWith("#casual")) { //A: solo incluir los que no empiezan con casual
			Tags.push(tag.titulo);
		}
		TagsTodos.push(tag.titulo);
	};
};

function traerUsuarios(){
	return $.ajax({ 
		type: 'GET',
		url:'/api/participante/?limit=4000',
	}).done( recordarUsuariosPk );
}

function recordarUsuariosPk(usuarios) { 
	let users = [];
	for (let user of usuarios.results) {
		users.push('@'+user.username+' '); //A: Se carga array con usuarios traidos desde la api
	}
	for (let usuario_pk of usuarios.results) {
		UsuariosPk[ usuario_pk.username ]= usuario_pk.pk; //A: Se carga array con usuarios y sus pk traidos desde la api
	}
	TagsYUsuarios = Tags.concat(users); //A: Se unifican arrays de usuarios y hashtags
	//DBG: console.log(TagsYUsuarios);
}
function traerDatos() {
	return traerTags().done(traerUsuarios);
}

/************************************************************************** */

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
	const el_destino= typeof(texto_dst)=="string" 
	? document.querySelector(texto_dst) 
	: texto_dst;
	//A: el_destino tiene un elemento
	
	if ('value' in el_destino) { //A: es input o textarea
		insertAtCursor(texto_dst, valor.value+' ');
	}
	else { //A: es otro elemento
		el_destino.innerHTML += valor.value + ' ';	
	}
}
    
function showTagButtons(pattern, tags_dst, texto_dst) { //U: para conectar con onKeyUp de un input, y pasarle el selector de la div donde aparecen los tags, y el textarea donde insertarlos
	var result = document.querySelector(tags_dst || '.result');
	let matching = getMatchingTags(pattern);
	result.innerHTML = htmlList(matching, texto_dst);
} 

traerTags();
traerUsuarios();

/************************************************************************** */

//Convertir hashtags y usuarios dentro del texto en links markdown



function hashtagAMarkdownLink(hashtag) {
	//TODO: revisar si es una charla que existe, sino devolverlo tal cual
	if (TagsTodos.indexOf(hashtag) > -1) { //A: el tag está en la lista de charlas
		return `[${hashtag}](/charla/${hashtag.slice(1)})` //A: con forma de link markdown
	}
	else {
		return hashtag;
	}
}		

function usuarioAMarkdownLink(usuario) {
	const username = usuario.slice(1);//A: sin @
	const pk = UsuariosPk[username];
	//DBG:console.log(usuario, JSON.stringify(username), pk, UsuariosPk	)
	if (pk!=null) { //A: el usuario existe
		return `[${usuario}](/como/${username})`; //A: con forma de link markdown si existia
	}
	else {
		return usuario; //A: no cambiamos nada
	}
}	

// S: votos ***************************************************
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function apiTextoACharlaGuardar(charlaitem, quiere_borrar) { //U: agrega un texto a una charla por su titulo, si no existe la crea
	//VER: https://docs.djangoproject.com/en/3.2/ref/csrf/#ajax
	try {
		const csrftoken = getCookie('csrftoken');
		const res= await fetch("/api/charlaitem/" + (quiere_borrar ? charlaitem.pk : ''), {
			method: quiere_borrar ? "DELETE" : "POST",
			headers: {
					'X-CSRFToken': csrftoken,
					"Accept": "application/json",
					"Content-Type": "application/json",
			},
			credentials: 'same-origin', 
			mode: "cors",
			body: JSON.stringify(charlaitem),
		});
		const res_data= quiere_borrar ? '' : await res.json();
		if (res_data==null || typeof(res_data)!='object') { res_data= {} }
		res_data.ok= res.ok;
	}
	catch (ex) {
		res_data= {ok: false};
	}
	console.log('apiTextoACharlaGuardar',charlaitem,res_data);
	return res_data;	
}

async function agregarAOtraCharlaClick(btn,texto_pk) { //U: cuando indico que algo me gusta
	//DBG: 
	console.log('agregarAOtraCharlaClick', btn, texto_pk); 
	ModalElegirCharlaOnOk_= async (charlasElegidasStr) => { //U: la llama el modal si apreto aceptar
		const charlas= charlasElegidasStr.split(/\s+/);	
		const promesas= charlas.map(charla => 
			apiTextoACharlaGuardar({charla_titulo: charla, texto_pk: texto_pk})
		);

		let hayErrores= false;
		try {
			const res= await Promise.all(promesas);
			hayErrores= ! res.every(r => r.texto_pk) //A: si se pudo guardar, todos los resultados tienen texto_pk	
		}
		catch (ex) {
			
		}
		if (hayErrores) { alert('No se pudo guardar.'); }
		else { $('#ModalElegirCharla').modal('hide'); }
	};
	$('#ModalElegirCharla').modal();	
}
