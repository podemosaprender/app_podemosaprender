#INFO: detectar hashtags para conectar charlas y textos
import re
LETRAS_CON_TILDE= 'áéíóúiüñÁÉÍÓÚÜÑ' #U: para encontrar
LETRAS_CON_TILDE_SIN_TILDE= 'aeiouiunAEIOUUN' #U: para reemplazar

def string_sin_tilde(s): #U: devuelve s con las letras con tilde reempazadas por las que no tienen
	return re.sub(
		f'[{LETRAS_CON_TILDE}]', 
		lambda m: LETRAS_CON_TILDE_SIN_TILDE[ LETRAS_CON_TILDE.index( m.group(0) ) ], 
		s
	)

#TEST: print(string_sin_tilde('Que gruñon ese Ñandú!'))


def hashtags_en(texto, quiere_sin_tildes= True):
	tags= set(re.findall(r'\B[@#][a-zA-Z'+LETRAS_CON_TILDE+'0-9_]+', texto))
	result= list(map(string_sin_tilde, tags)) if quiere_sin_tildes else tags
	return result
	
#TEST: print(hashtags_en('#HastagAlPrincipio porque esto es #UnaPrueba y tiene\notro renglon para @mauriciocap pero no x@gmail.com con #este_hashtag_recampeón que agregue. Si repito #UnaPrueba pero no es #UnaPruebaÑoña no lo devuelve dos veces en la lista @alguien_al_final'))
