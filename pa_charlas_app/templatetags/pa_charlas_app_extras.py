#INFO: nuestros propios tags y filtros para las plantillas
#VER: https://docs.djangoproject.com/en/3.1/howto/custom-template-tags/

from django import template
from django import urls
import logging
logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def addstr(arg1, arg2):
	"""concatenate arg1 & arg2"""
	return str(arg1) + str(arg2)

@register.simple_tag(takes_context=True)
def url_full(context,view,*args,**kwargs): #U: url con protocolo, host, puerto, ... para permalinks
	logger.debug(f'url_full {view} {kwargs}')
	uri= context.request.build_absolute_uri( urls.reverse(view, kwargs= kwargs) ) 
	logger.debug(f'url_full {view} {kwargs} {uri}')
	return uri
