#INFO: nuestros propios tags y filtros para las plantillas
#VER: https://docs.djangoproject.com/en/3.1/howto/custom-template-tags/

from django import template
from django import urls
import re

import logging
logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def addstr(arg1, arg2):
	"""concatenate arg1 & arg2"""
	return str(arg1) + str(arg2)

@register.filter
def re_match(arg1, arg2):
	"""return data for other filter then_..."""
	return ['match',arg1,arg2] #A: devuelvo un array que va a usar el filtro que sigue

@register.filter
def then_sub(arg1, arg2):
	"""mistrvar|re_match:'#(.*)'|then_sub:''"""
	return re.sub(str(arg1[2]), str(arg2), str(arg1[1])) 

@register.filter
def at_key(a_dict, key):
	"""Return element at key"""
	return a_dict[key]

@register.simple_tag
def define(val=None):
	"""Use as {% define expr as varname %}"""
	return val

@register.simple_tag(takes_context=True)
def url_full(context,view,*args,**kwargs): #U: url con protocolo, host, puerto, ... para permalinks
	logger.debug(f'url_full {view} {kwargs}')
	uri= context.request.build_absolute_uri( urls.reverse(view, kwargs= kwargs) ) 
	logger.debug(f'url_full {view} {kwargs} {uri}')
	return uri

