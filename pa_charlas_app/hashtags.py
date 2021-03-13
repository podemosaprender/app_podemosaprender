#INFO: detectar hashtags para conectar charlas y textos
import re
def hashtags_en(texto):
	return set(re.findall('#[a-zA-Z0-9_]+', texto))
	
#print(hashtags_en('esto es #UnaPrueba y tiene\notro renglon con #este_hashtag que agregue. Si repito #UnaPrueba no lo devuelve dos veces en la lista'))
