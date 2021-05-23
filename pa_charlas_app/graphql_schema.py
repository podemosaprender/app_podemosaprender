#INFO: punto de entrada a la api graphql
#VER: https://docs.graphene-python.org/projects/django/en/latest/installation/
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from django.core.exceptions import PermissionDenied

from .graphql_util import ListaRelayConOrderBy
from .models import *


# S: nuestra API ###########################################
#VER: https://docs.graphene-python.org/projects/django/en/latest/queries/
class UserNode(DjangoObjectType):
	class Meta:
		model = User
		fields = ('id','username')

class TextoNode(DjangoObjectType): #U: 
	name= graphene.String()
	class Meta:
		model = Texto
		fields = '__all__'
		filter_fields = {
			'de_quien__username': ['exact'],
			'fh_creado': ['gt'],
		}
		interfaces = (relay.Node, ) #VER: https://docs.graphene-python.org/projects/django/en/latest/filtering/

class BancoTxNode(DjangoObjectType): #U: 
	class Meta:
		model = BancoTx
		fields = '__all__'
		filter_fields = {
			'fh_creado': ['gt'],
		}
		interfaces = (relay.Node, ) #VER: https://docs.graphene-python.org/projects/django/en/latest/filtering/

class Consultas(graphene.ObjectType):
	hola = graphene.String(default_value='PodemosAprender', description='Devuelve "PodemosAprender"')
	#U: fetchData('http://127.0.0.1:8000/graphql',{method:'POST', headers: { 'Content-Type': 'application/json'}, body: JSON.stringify({"query":"{ hola }\n\n","variables":null})}, x => console.log(JSON.stringify(x.data,null,1),x))

	texto = relay.Node.Field(TextoNode) #U: { texto(id: "VGV4dG9Ob2RlOjE=") {  id, fhCreado, texto } } 
	texto_all = ListaRelayConOrderBy(TextoNode)
	#U: { textoAll { edges { node { id, fhCreado, deQuien { id, username }, texto } } } }
	#U: { textoAll(deQuien_Username: "pepita") { edges { node { id, fhCreado, texto } } } }
	#U: { textoAll(orderBy: ["-fhCreado"]) { edges { node { id, fhCreado, texto } } } }
	#U: { textoAll(orderBy: ["-fhCreado"]) { edges { node { id, fhCreado, texto } } } }
	#VER: https://graphql.org/learn/pagination/

	bancoTx = relay.Node.Field(BancoTxNode)
	bancoTx_all = ListaRelayConOrderBy(BancoTxNode)

	def resolve_hola(self, info, **kwargs): #U: para probar si estamos autenticados
		return f'Hola {info.context.user.username}! PodemosAprender!'

	def resolve_texto_all(self, info, **kwargs):
		print(f'resolve_texto_all {info.context.user}')
		if info.context.user.is_authenticated:
			print(f'User {info.context.user}')
			return Texto.objects.all()
		else:
			raise PermissionDenied('No tenes permisos')	

class Modificaciones(graphene.ObjectType):
	pass

schema = graphene.Schema(query=Consultas) #, mutation=Modificaciones)
