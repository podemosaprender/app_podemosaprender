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

function copyToClipboardEl(selector, ev) {
	var txt= document.querySelector(selector).innerText
	console.log(ev)
	var permalink= location.href
	copyToClipboard('De '+permalink+'\n'+txt)
	if (ev) { ev.preventDefault(); } //A: no navegar
	return false; //A: no navegar
}
