#INFO: punto de entrada a la api graphql
#VER: https://docs.graphene-python.org/projects/django/en/latest/installation/
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_relay import from_global_id
import django_filters

from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from datetime import datetime

from .graphql_util import ListaRelayConOrderBy

from .forms import TextoForm
from .models import *


# S: nuestra API ###########################################
#VER: https://docs.graphene-python.org/projects/django/en/latest/queries/
class UserNode(DjangoObjectType):
	class Meta:
		model = User
		fields = ('id','username')

#VER: https://django-filter.readthedocs.io/en/stable/guide/usage.html#the-filter
class TextoFilterSet(django_filters.FilterSet): #U: para texto necesitamos mas detalles
	charla__titulo= django_filters.CharFilter(method='filter_enCharla')

	def filter_enCharla(self, queryset, name, value):
		qCharlaItem= CharlaItem.objects.filter(charla__titulo= value).values('texto_id')
		return queryset.filter(id__in= qCharlaItem)

	class Meta:
		model = Texto
		fields = {
			'fh_creado': ['gt','lt'],
			'fh_editado': ['gt','lt'],
			'de_quien__username': ['exact'],
		}

class TextoNode(DjangoObjectType): 
	class Meta:
		model = Texto
		fields = '__all__'

		interfaces = (relay.Node, ) #VER: https://docs.graphene-python.org/projects/django/en/latest/filtering/


class CharlaFilterSet(django_filters.FilterSet): 
	participa__username= django_filters.CharFilter(method='filter_participa')

	def filter_participa(self, queryset, name, value):
		return (
			queryset
			.filter(charlaitem__texto__de_quien__username=value)
			.distinct()
		)

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

class CharlaItemFilterSet(django_filters.FilterSet): 
	deQuien__username= django_filters.CharFilter(method='filter_deQuien')
	charla__titulo= django_filters.CharFilter(method='filter_titulo')

	def filter_deQuien(self, queryset, name, value):
		return queryset.filter(texto__de_quien__username= value)

	def filter_titulo(self, queryset, name, value):
		return queryset.filter(charla__titulo= value)

	class Meta:
		model= CharlaItem
		fields = {
			'texto_id': ['exact'],
			'charla_id': ['exact'],
			'orden': ['exact','icontains','contains','startswith'],
			#'charla__titulo': ['exact','icontains','startswith'],
		}

class CharlaItemNode(DjangoObjectType):
	class Meta:
		model = CharlaItem	
		fields = '__all__'
		filter_fields = {
			'texto_id': ['exact'],
			'charla_id': ['exact'],
			'orden': ['exact','icontains','contains','startswith'],
			'charla__titulo': ['exact','icontains','startswith'],
		}
		interfaces = (relay.Node, ) #VER: https://docs.graphene-python.org/projects/django/en/latest/filtering/

class Consultas(graphene.ObjectType):
	hola = graphene.String(default_value='PodemosAprender', description='Devuelve "PodemosAprender"')
	#U: fetchData('http://127.0.0.1:8000/graphql',{method:'POST', headers: { 'Content-Type': 'application/json'}, body: JSON.stringify({"query":"{ hola }\n\n","variables":null})}, x => console.log(JSON.stringify(x.data,null,1),x))

	texto = relay.Node.Field(TextoNode) #U: { texto(id: "VGV4dG9Ob2RlOjE=") {  id, fhCreado, texto } } 
	texto_lista = ListaRelayConOrderBy(TextoNode, filterset_class= TextoFilterSet)
	#U: { textoLista { edges { node { id, fhCreado, deQuien { id, username }, texto } } } }
	#U: { textoLista(deQuien_Username: "pepita") { edges { node { id, fhCreado, texto } } } }
	#U: { textoLista(orderBy: ["-fhCreado"]) { edges { node { id, fhCreado, texto } } } }
	#U: { textoLista(orderBy: ["-fhCreado"]) { edges { node { id, fhCreado, texto } } } }
	#VER: https://graphql.org/learn/pagination/

	charla = relay.Node.Field(CharlaNode)
	charla_lista = ListaRelayConOrderBy(CharlaNode, filterset_class= CharlaFilterSet)

	charlaitem = relay.Node.Field(CharlaItemNode)
	charlaitem_lista = ListaRelayConOrderBy(CharlaItemNode, filterset_class= CharlaItemFilterSet)
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


class TextoModificar(relay.ClientIDMutation):
	texto = graphene.Field(TextoNode)

	class Input:
		texto = graphene.String(required=True)
		id = graphene.ID(required=False)
		charla_titulo = graphene.String(required=False)
		orden = graphene.String(required=False)

	@classmethod
	def mutate_and_get_payload(cls, root, info, texto, id=None, charla_titulo=None, orden= None):
		if not info.context.user.is_authenticated:
			raise PermissionDenied('No tenes permisos')	

		elTextoExistenteId= None #DFLT
		elTextoExistente= None #DFLT
		if not id is None:
			elTextoExistenteId= from_global_id(id)[1]
			elTextoExistente= get_object_or_404(Texto, pk= elTextoExistenteId )

		#DBG:print(f'TextoModificar id={id} texto={texto}')
		textoForm= TextoForm({'texto': texto}, instance= elTextoExistente)
		if not textoForm.is_valid():
			raise ValidationError(textoForm.errors)

		item= texto_guardar(textoForm, info.context.user, charla_titulo=charla_titulo, orden=orden)
		#DBG: print(f'TextoModificar id={elTextoExistenteId} vs. guarde {item.id}')

		return TextoModificar(texto=item)


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
	texto_modificar = TextoModificar.Field();
	#U: mutation pruebaTexto { textoModificar(input: {texto: "otro va en #bandadjango", id: "VGV4dG9Ob2RlOjcz"}) { clientMutationId texto { id texto fhCreado fhEditado } } }

	charlaitem_crear = CharlaItemModificar.Field()	
	#U: mutation miMutacion { charlaitemCrear(input: {textoId: "VGV4dG9Ob2RlOjE=", charlaTitulo: "#bandadjango"}) { charlaitem { id, texto { id, texto }, } } }

schema = graphene.Schema(query=Consultas, mutation=Modificaciones)
