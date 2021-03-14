#INFO: nuestros propios tags y filtros para las plantillas
#VER: https://docs.djangoproject.com/en/3.1/howto/custom-template-tags/

from django import template

register = template.Library()

@register.filter
def addstr(arg1, arg2):
	"""concatenate arg1 & arg2"""
	return str(arg1) + str(arg2)

