#SEC: manejamos login_required en urls.py

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User

from django import forms
import re
import os

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

# S: texto como imagen ####################################

import cairosvg

def texto_img(request, pk=None): #U: imagen con texto para og:image que se muestra en Facebook
	texto= get_object_or_404(Texto, pk=pk) 

	tpl_path= os.path.normpath(os.path.abspath(__file__)+'/../templates/pa_charlas_app/og_image1.svg')
	with open(tpl_path,'r') as f:
		tpl= f.read()
	#A: leimos un svg como plantilla, tiene marcas TPL1 a TPL6 para lineas de texto
	
	W= 28 #U: cuantas letras entran en una linea, TODO: elegir y hacer configurable
	LMAX= 8 #U: cuantas lineas en una og image

	lineas= [] #U: el texto para mostrar separado en lineas

	texto_norm= re.sub(r'\s+',' ',texto.texto)
	tokens= re.split(r'([\s\n])', texto_norm)
	linea_num= 0 #U: por que linea voy
	linea= '' #U: esta linea
	for tk in tokens:
		#DBG: print(tk, len(linea)+ len(tk)+1)
		if tk=='\n' or len(linea)+ len(tk)+1> W: #A: aparecio fin de linea o se acabo el espacio
			lineas.append(' '*((W-len(linea)) // 2)+ linea)	
			linea_num+=1
			if linea_num>LMAX:
				break
			if tk!=' ' and tk!='\n':
				linea= tk
			else:
				linea=''
		else:
			linea+=tk
	if not linea_num>LMAX:
		lineas.append(' '*((W-len(linea)) // 2)+ linea)	
		
	margen= max(LMAX-len(lineas),0) // 2
	for linea_num in range(0,LMAX+1):
			idx= linea_num - margen
			tpl= tpl.replace(f'TPL{linea_num}', 
				lineas[linea_num-margen] if 0 <= idx and idx < len(lineas) else ''
			)

	img_bytes= cairosvg.svg2png(tpl)
	return HttpResponse( img_bytes, content_type='image/png')


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
	queryset=  Charla.objects.order_by('titulo').all()
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
	return render(request, 'pa_charlas_app/texto_list.html', {'object_list': textos, 'charla': charla, 'titulo': charla.titulo, 'puede_crear': True })

# S: Lista de usuarios ####################################

def usuario_list(request):
	usuarios = User.objects.all()
	return render(request, 'pa_charlas_app/usuario_list.html',{'object_list': usuarios, 'titulo':'usuarios' })


def usuario_texto_list(request, username=None, pk=None): #U: los textos de UNA charla, btn para agregar
	if not pk is None:
		user= get_object_or_404(User, pk=pk)
	else:
		user= get_object_or_404(User, username= username)
	textos= Texto.objects.filter(de_quien=user).order_by('fh_creado').all()
	return render(request, 'pa_charlas_app/texto_list.html', {'object_list': textos, 'titulo': user.username})
