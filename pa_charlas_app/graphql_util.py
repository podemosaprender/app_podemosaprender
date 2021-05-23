#INFO: herramientas para usar mas comodo graphene

import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene.utils.str_converters import to_snake_case

from django.core.exceptions import PermissionDenied

import re

# S: autenticar con el mismo token de django rest ################

#TODO: en algun momento vamos a QUITAR DRF y usar solo graphene, pero mientras mantenemos compatibilidad

#VER: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/rest_framework_simplejwt.html
from rest_framework_simplejwt.authentication import JWTAuthentication

#VER: https://docs.graphene-python.org/en/latest/execution/middleware/
DRF_JWT_Authenticator= JWTAuthentication() #U: instancia para autenticar

def auth_middleware(next, root, info, **args):
	confirmamosPuedeSeguir = False #DFLT

	request= info.context #U: alias, por claridad
	hostDeberiaSer= request.META.get('HTTP_HOST','si.podemosaprender.org') #U: el nombre donde publicamos ej localhost:8000

	try:
		jwt_data= DRF_JWT_Authenticator.authenticate(request)
		#DBG: print(f'graphql auth drf_jwt {jwt_data}')
		if not jwt_data is None: #A: tenia token valido
			(user, token)= jwt_data
			confirmamosPuedeSeguir= True
			info.context.user= user #A: tomo el usuario activo del token
	except:
		pass #A: no tenia token o expiro

	#VER: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#verifying-origin-with-standard-headers
	if not confirmamosPuedeSeguir: #A: tenemos que revisar si viene de nuestra pagina para evitar CSRF
		originDice= request.META.get('HTTP_ORIGIN','') #A: este el navegador no lo deja modificar ej en fecth	
		refererDice= request.META.get('HTTP_REFERER','') #A: este el navegador no lo deja modificar ej en fecth	

		originOk= re.match(f'^https?://{hostDeberiaSer}$',originDice)	and True
		refererOk= re.match(f'^https?://{hostDeberiaSer}(/.*)$',refererDice) and True

		confirmamosPuedeSeguir= refererOk and originOk
		print(f'graphql auth host={hostDeberiaSer} origin={originDice} originOk={originOk}  referer={refererDice} refererOk={refererOk}')
	
	if confirmamosPuedeSeguir:
		return_value = next(root, info, **args)
		return return_value
	else:
		raise PermissionDenied(f'Solo podes acceder con un token o desde nuestro sitio {hostDeberiaSer}')


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

def ListaRelayConOrderBy(tipoNode, filterset_class= None): #U: para que tenga filtros y orderBy
	return OrderedDjangoFilterConnectionField_2_6(
		tipoNode, 
		orderBy=graphene.List(of_type=graphene.String),
		filterset_class= filterset_class
	) 


