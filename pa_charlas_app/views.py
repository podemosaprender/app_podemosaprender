from django.shortcuts import render
from .models import Texto

# Create your views here.
def texto_list(request):
	textos = Texto.objects.order_by('fh_creado')
	return render(request, 'pa_charlas_app/texto_list.html', {'textos': textos})
