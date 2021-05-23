from pa_charlas_app.models import *

def run():
	items= CharlaItem.objects.filter(charla__titulo__contains='borrame')

	Texto.objects.filter(pk__in=items.values('texto__id')).delete()

	Charla.objects.filter(titulo__contains='borrame').delete()

