#SEC: manejamos login_required en urls.py

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.utils import timezone

from django import forms

from .models import Texto, Charla, texto_guardar
from .forms import TextoForm

import json
import base64

import logging
logger = logging.getLogger(__name__)

def enc_b64_o(o): #U: codificar objeto como json base64
	return base64.b64encode(json.dumps(o).encode('utf-8')).decode('ascii')
def enc_b64_o_r(s, dflt=None): #U: decodificar json base64
	return json.loads(base64.b64decode(s)) if not s is None else dflt

# S: sesion ################################################
def login(request): #U: pantalla de login con botones de google, facebook, etc
  return render(request, 'pa_charlas_app/login.html')

# S: textos ################################################

def texto_edit(request, pk=None, charla_pk=None): #U: crear Y editar textos, de charlas o para empezar una
	texto= None #DFLT, nuevo
	if not pk is None:
		texto= get_object_or_404(Texto, pk=pk) 

	if request.method == "POST":
		form= TextoForm(request.POST, instance= texto)
		if form.is_valid():
			extra_data= enc_b64_o_r(request.POST.get('extra_form_data'),{})
			texto= texto_guardar(form, request.user, extra_data.get('charla'))
			#A: si no le pase una charla y no existia, crea una "casual"
			logger.debug(f'VW texto {request.user.username} {extra_data}')
			return redirect(extra_data.get('volver_a') or '/')
	else:
		viene_de= request.META.get('HTTP_REFERER')
		form = TextoForm(instance= texto, initial={'viene_de': 'que_pasa'})
		extra_data= {'charla': charla_pk, 'volver_a': viene_de}
		return render(
			request, 
			'pa_charlas_app/base_edit.html', 
			{
				'form': form, 
				'extra_form_data': enc_b64_o(extra_data),
			})

def texto_detail(request, pk=None): #U: ver un texto para compartir en las redes
	texto= get_object_or_404(Texto, pk=pk) 
	return render(request, 'pa_charlas_app/texto_detail.html', {'texto': texto})

# S: Charlas ###############################################

class CharlaListView(ListView): #U: la lista de charlas
	template_name= 'pa_charlas_app/charla_list.html'
	model = Charla
	paginate_by = 20  
	extra_context= {
		'type_name': 'charla',
		'type_url_base': 'charla',
		'create_url': '/charla/nueva',
		'titulo': 'Charlas',
		'vista_detalle': 'charla_texto_list_k',
	}

# S: Charla vista comoda ##################################
def charla_texto_list(request, charla_titulo=None, pk=None): #U: los textos de UNA charla, btn para agregar
	if not pk is None:
		charla= get_object_or_404(Charla, pk=pk)
	else:
		charla= get_object_or_404(Charla, titulo= '#'+charla_titulo)
	textos= charla.textos.order_by('fh_creado').all()
	return render(request, 'pa_charlas_app/texto_list.html', {'object_list': textos, 'charla': charla, 'titulo': charla.titulo})
