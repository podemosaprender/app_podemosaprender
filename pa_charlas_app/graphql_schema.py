#INFO: punto de entrada a la api graphql
#VER: https://docs.graphene-python.org/projects/django/en/latest/installation/
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import *

from graphene.utils.str_converters import to_snake_case

# S: orderBy ###############################################
#FROM: https://gist.github.com/ivlevdenis/3fb0ede89650889cc9f62a77770e7156
class OrderedDjangoFilterConnectionField(DjangoFilterConnectionField):
	@classmethod
	def connection_resolver(cls, resolver, connection, default_manager, max_limit,
							enforce_first_or_last, filterset_class, filtering_args,
							root, args, context, info):
		print(f'OrderBy {args}')
		filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
		qs = default_manager.get_queryset()
		qs = filterset_class(data=filter_kwargs, queryset=qs).qs
		order = args.get('orderBy', None)
		if order:
			qs = qs.order_by(*order)
		return super(DjangoFilterConnectionField, cls).connection_resolver(resolver, connection, qs, max_limit, enforce_first_or_last, root, args, context, info)

class OrderedDjangoFilterConnectionField_2_1_rc(DjangoFilterConnectionField):
	@classmethod
	def connection_resolver(cls, resolver, connection, default_manager, max_limit,
							enforce_first_or_last, filterset_class, filtering_args,
							root, info, **args):
		print(f'OrderBy {args}')
		filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
		qs = default_manager.get_queryset() if hasattr(default_manager, 'get_queryset') else default_manager
		qs = filterset_class(data=filter_kwargs, queryset=qs).qs
		order = args.get('orderBy', None)
		if order:
			qs = qs.order_by(*order)
		return super(DjangoFilterConnectionField, cls).connection_resolver(resolver, connection, qs, max_limit,
																			 enforce_first_or_last, root, info, **args)

#FROM: https://stackoverflow.com/questions/57478464/django-graphene-relay-order-by-orderingfilter/61543302#61543302
class OrderedDjangoFilterConnectionField_2_6(DjangoFilterConnectionField):
	@classmethod
	def resolve_queryset(
		cls, connection, iterable, info, args, filtering_args, filterset_class
	):
		print(f'OrderBy {args}')
		qs = super(DjangoFilterConnectionField, cls).resolve_queryset(
			connection, iterable, info, args
		)
		filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
		qs = filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

		order = args.get('orderBy', None)
		if order:
			if type(order) is str:
				snake_order = to_snake_case(order)
			else:
				snake_order = [to_snake_case(o) for o in order]
			qs = qs.order_by(*snake_order)
		return qs

def ListaRelayConOrderBy(tipoNode): #U: para que tenga filtros y orderBy
	return OrderedDjangoFilterConnectionField_2_6(tipoNode, orderBy=graphene.List(of_type=graphene.String)) 

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

class Consultas(graphene.ObjectType):
	hola = graphene.String(default_value='PodemosAprender', description='Devuelve "PodemosAprender"')
	texto = relay.Node.Field(TextoNode) #U: { texto(id: "VGV4dG9Ob2RlOjE=") {  id, fhCreado, texto } } 
	texto_all = ListaRelayConOrderBy(TextoNode)
	#U: { textoAll { edges { node { id, fhCreado, deQuien { id, username }, texto } } } }
	#U: { textoAll(deQuien_Username: "pepita") { edges { node { id, fhCreado, texto } } } }
	#U: { textoAll(orderBy: ["-fhCreado"]) { edges { node { id, fhCreado, texto } } } }
	#U: { textoAll(orderBy: ["-fhCreado"]) { edges { node { id, fhCreado, texto } } } }
	#VER: https://graphql.org/learn/pagination/

class Modificaciones(graphene.ObjectType):
	pass

schema = graphene.Schema(query=Consultas) #, mutation=Modificaciones)
