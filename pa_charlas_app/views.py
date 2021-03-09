from django.shortcuts import render, get_object_or_404
from .models import Texto

# Create your views here.
def texto_list(request):
	textos = Texto.objects.order_by('fh_creado')
	return render(request, 'pa_charlas_app/texto_list.html', {'textos': textos})

def texto_detail(request, pk):
	texto = get_object_or_404(Texto, pk=pk)
	permalink = request.get_raw_uri() #TODO: buscar una forma mejor, configuracion?
	return render(request, 'pa_charlas_app/texto_detail.html', {'texto': texto, 'permalink': permalink})
