from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Texto
from .forms import TextoForm


# Create your views here.
def texto_list(request):
	textos= Texto.objects.order_by('fh_creado')
	return render(request, 'pa_charlas_app/texto_list.html', {'textos': textos})

def texto_detail(request, pk):
	texto= get_object_or_404(Texto, pk=pk)
	permalink= request.get_raw_uri() #TODO: buscar una forma mejor, configuracion?
	return render(request, 'pa_charlas_app/texto_detail.html', {'texto': texto, 'permalink': permalink})

def texto_edit(request, pk=None): #U: sirve para crear Y editar
	texto= None #DFLT, nuevo
	if not pk is None:
		texto= get_object_or_404(Texto, pk=pk) 

	if request.method == "POST":
		form= TextoForm(request.POST, instance= texto)
		if form.is_valid():
			texto= form.save(commit=False)
			texto.de_quien= request.user
			texto.fh_creado= timezone.now()
			texto.save()
			return redirect('texto_detail', pk=texto.pk)
	else:
		form = TextoForm(instance= texto)
		return render(request, 'pa_charlas_app/texto_edit.html', {'form': form})

