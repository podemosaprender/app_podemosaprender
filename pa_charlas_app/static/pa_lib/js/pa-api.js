//INFO: API REST CON TOKEN en si.podemosaprender.org
// escribo funciones que se puedan probar por separado, despues las junto

export const CFG = {
	api_url: 'https://si.podemosaprender.org', //U: para usar otro servidor si queres
}

//S: guardar el token aunque se cierre la app o pagina
export function tokenGuardar(tokens, usuario) {
  //U: guarda los tokens aunque cargue de nuevo la pagina/app
  localStorage.tokens = JSON.stringify(tokens);
  localStorage.usuario = usuario;
}

export function tokenLeer() {
  //U: lee los tokens que tenia guardados
  var result;
  try {
    result = JSON.parse(localStorage.tokens);
  } catch {} //A: me ocupo mas abajo

  if (result != null && typeof result != "object") {
    //A: no es valido, se guardo algo raro en localStorage ej mientras programaba
    result = null; //A: no lo uso
  }

  return result;
}

export function usuarioLeer() {
  //U: lee el usuario que tenia guardado
  return localStorage.usuario;
}

export function tokenBorrar() {
  //U: ej para cerrar sesion en navegador publico
  localStorage.tokens = '';
  localStorage.usuario = '';
  //TODO: ademas deberia invalidarlo en el servidor
}

//S: en esta parte SOLAMENTE accedo a la API
export async function apiTokenConseguir(usr, pass) {
  //U: se autentica con usuario y clave para conseguir un token
  const res = await fetch(CFG.api_url + "/api/token/", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: usr, password: pass }),
  });
  const resData = await res.json();
  return resData;
}

export async function apiTokenNoSirve(tokenAccess) {
  //U: null o por que no sirve
  const res = await fetch(CFG.api_url + "/api/token/verify/", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token: tokenAccess }),
  });
  const resData = await res.json();
  const sirveP = //A: devuelvo true si cumple todas las condiciones
    resData != null &&
    typeof resData == "object" &&
    Object.keys(resData).length == 0;
  return sirveP ? null : resData; //A: null si sirve, sino la razon
}

export async function apiTokenRenovar(tokenRefresh) {
  //U: null o por que no sirve
  const res = await fetch(CFG.api_url + "/api/token/refresh/", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh: tokenRefresh }),
  });
  const resData = await res.json();
  return resData; //A: null si sirve, sino la razon
}

//S: integro acceso a la api y guardar localmente
export async function apiLogin(usr, pass) {
	try {
		const res = await apiTokenConseguir(usr, pass);
		if (res.access) { //A: fue bien
			tokenGuardar(res, usr);
			return {}; //A: si no hay detail ni error es ok
		}
		else {
			return {...res, error: res.detail || 'error desconocido'};
		}
	}
	catch (ex) {
		return {error: ex.message || 'error desconocido'}
	}
}

export async function apiLogout() {
	tokenBorrar();
	//TODO: invalidarlo en el servidor, por eso la declaramos async
	return true;
}

export async function apiNecesitoLoginP() {
  var result = true; //DFLT, necesito login
  const tokX = tokenLeer();
  if (tokX != null && tokX.refresh) {
    //A: tengo datos guardados y un token para refrescar
    const tokFresco = await apiTokenRenovar(tokX.refresh);
    if (tokFresco.access) {
      //A: bien, consegui un token fresco}
      tokX.access = tokFresco.access;
      tokenGuardar(tokX, usuarioLeer());
      result = false; //A: no necesito login
    }
  }
  return result;
}

const ErrorMsgNecesitaLogin= 'PaApi fetchConToken no tengo token, llamaste apiLogin?';

export async function fetchConToken(data, opciones, url, noQuiereJson) { //U: hace fetch agregando token, y con defaults
  //U: agrega el token a un fetch
  const tok = tokenLeer();
  if (!tok || !tok.access) {
    throw new Error(ErrorMsgNecesitaLogin);
  }

	url= url || '/graphql'; //DFLT 
	if (! url.startsWith('http') ) {
		url= CFG.api_url+url;
	}

  opciones = opciones || {};
  opciones.headers = opciones.headers || {};
  opciones.headers.Authorization = "Bearer " + tok.access;

	if (data!=null) {
		if (typeof(data)=='object') {
			opciones.body= JSON.stringify(data);
		}
		else {
			opciones.body= data;
		}
		opciones.method= opciones.method || 'POST';
		opciones.headers= opciones.headers || {};
		opciones.headers['Content-Type']= opciones.headers['Content-Type'] || 'application/json';
	}	

	//TODO: excepcion token expiro?
  const res= await fetch(url, opciones);
	if (noQuiereJson) { 
		return res;
	}
	else {
		const data= await res.json();
		return data;
	}
}
//TEST: fetchConToken('https://si.podemosaprender.org/api/token/user/').then(console.log)
// Object { user: "mauriciocap", auth: "eyJ0eXA..." }

//#########################################################################################################

/* U: consultar textos via graphql

fetchData('http://127.0.0.1:8000/graphql',{method:'POST', headers: {
      'Content-Type': 'application/json'}, body: JSON.stringify({"query":"{ textoAll(orderBy: [\"-fhCreado\"], first: 2, offset: 10) { edges { node { id, fhCreado, texto } } } }\n\n","variables":null})}, x => console.log(JSON.stringify(x.data,null,1)))

*/

export function esErrorNecesitaLogin(ex) {
	return ex.message === ErrorMsgNecesitaLogin;
}

export default { fetchConToken, apiLogin, apiLogout, CFG, esErrorNecesitaLogin }
