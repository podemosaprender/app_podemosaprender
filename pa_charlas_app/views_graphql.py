#INFO: punto de entrada a la api graphql
#VER: https://docs.graphene-python.org/projects/django/en/latest/installation/
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_relay import from_global_id
from django.core.exceptions import PermissionDenied
from datetime import datetime

from .graphql_util import ListaRelayConOrderBy
from .models import *


# S: nuestra API ###########################################
#VER: https://docs.graphene-python.org/projects/django/en/latest/queries/
class UserNode(DjangoObjectType):
	class Meta:
		model = User
		fields = ('id','username')

class TextoNode(DjangoObjectType): 
	class Meta:
		model = Texto
		fields = '__all__'
		filter_fields = {
			'de_quien__username': ['exact'],
			'fh_creado': ['gt','lt'],
		}
		interfaces = (relay.Node, ) #VER: https://docs.graphene-python.org/projects/django/en/latest/filtering/

class CharlaNode(DjangoObjectType):
	class Meta:
		model = Charla
		fields = '__all__'
		filter_fields = {
			'de_quien__username': ['exact'],
			'fh_creado': ['gt','lt'],
			'titulo': ['icontains'],
		}
		interfaces = (relay.Node, ) #VER: https://docs.graphene-python.org/projects/django/en/latest/filtering/

class CharlaItemNode(DjangoObjectType):
	class Meta:
		model = CharlaItem	
		fields = '__all__'
		filter_fields = {
			'texto_id': ['exact'],
			'charla_id': ['exact'],
			'charla__titulo': ['exact','icontains'],
		}
		interfaces = (relay.Node, ) #VER: https://docs.graphene-python.org/projects/django/en/latest/filtering/

class Consultas(graphene.ObjectType):
	hola = graphene.String(default_value='PodemosAprender', description='Devuelve "PodemosAprender"')
	#U: fetchData('http://127.0.0.1:8000/graphql',{method:'POST', headers: { 'Content-Type': 'application/json'}, body: JSON.stringify({"query":"{ hola }\n\n","variables":null})}, x => console.log(JSON.stringify(x.data,null,1),x))

	texto = relay.Node.Field(TextoNode) #U: { texto(id: "VGV4dG9Ob2RlOjE=") {  id, fhCreado, texto } } 
	texto_lista = ListaRelayConOrderBy(TextoNode)
	#U: { textoLista { edges { node { id, fhCreado, deQuien { id, username }, texto } } } }
	#U: { textoLista(deQuien_Username: "pepita") { edges { node { id, fhCreado, texto } } } }
	#U: { textoLista(orderBy: ["-fhCreado"]) { edges { node { id, fhCreado, texto } } } }
	#U: { textoLista(orderBy: ["-fhCreado"]) { edges { node { id, fhCreado, texto } } } }
	#VER: https://graphql.org/learn/pagination/

	charla = relay.Node.Field(CharlaNode)
	charla_lista = ListaRelayConOrderBy(CharlaNode)

	charlaitem = relay.Node.Field(CharlaItemNode)
	charlaitem_lista = ListaRelayConOrderBy(CharlaItemNode)
	#U: { charlaitemLista(charla_Titulo_Icontains: "banda") { edges { node { id, charla { titulo }, texto { texto }} }}}

	def resolve_hola(self, info, **kwargs): #U: para probar si estamos autenticados
		return f'Hola {info.context.user.username}! PodemosAprender!\nSon las {datetime.now()}.'

	def resolve_texto_lista(self, info, **kwargs):
		if info.context.user.is_authenticated:
			print(f'User {info.context.user}')
			return Texto.objects.select_related('de_quien').all()
		else:
			raise PermissionDenied('No tenes permisos')	

	def resolve_charla_lista(self, info, **kwargs):
		if info.context.user.is_authenticated:
			print(f'User {info.context.user}')
			return Charla.objects.all()
		else:
			raise PermissionDenied('No tenes permisos')	

	def resolve_charlaitem_lista(self, info, **kwargs):
		#DBG: print(f'resolve_charlaitem_lista {info.context.user}')
		if info.context.user.is_authenticated:
			return CharlaItem.objects.select_related('charla').select_related('texto').all()
		else:
			raise PermissionDenied('No tenes permisos')	


class CharlaItemModificar(relay.ClientIDMutation):
	charlaitem = graphene.Field(CharlaItemNode)

	class Input:
		texto_id = graphene.ID(required=True)
		charla_titulo = graphene.String(required=True)
		orden = graphene.String()

	@classmethod
	def mutate_and_get_payload(cls, root, info, texto_id, charla_titulo, orden=None):
		texto_pk= from_global_id(texto_id)[1]
		charlaitem = CharlaItem() 
		charlaitem.texto= Texto.objects.get(pk=texto_pk)
		charlaitem.charla= Charla.objects.get(titulo= charla_titulo)
		charlaitem.orden= orden
		return CharlaItemModificar(charlaitem=charlaitem)

class Modificaciones(graphene.ObjectType):
	charlaitem_crear = CharlaItemModificar.Field()	
	#U: mutation miMutacion { charlaitemCrear(input: {textoId: "VGV4dG9Ob2RlOjE=", charlaTitulo: "#bandadjango"}) { charlaitem { id, texto { id, texto }, } } }

schema = graphene.Schema(query=Consultas, mutation=Modificaciones)
