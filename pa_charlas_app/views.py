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
import datetime

from .models import Texto, Charla, Visita, charla_participantes, texto_guardar
from .forms import TextoForm

import json
import base64

import logging
logger = logging.getLogger(__name__)

def enc_b64_o(o): #U: codificar objeto como json base64
	return base64.b64encode(json.dumps(o).encode('utf-8')).decode('ascii')
def enc_b64_o_r(s, dflt=None): #U: decodificar json base64
	return json.loads(base64.b64decode(s)) if not s is None else dflt

def z1_to_hex(zero_to_one_values_list): #U: covierte una lista de valores 0 a 1 en hex 0-255
	return ''.join(list(map(lambda v: f'{int(v*255):02x}', list(zero_to_one_values_list))))

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
	
	import colorsys
	import random
	BgColor_cnt = 20 #A: cuantos colores de fondo distintos
	hue= random.randint(1, BgColor_cnt)*1.0/BgColor_cnt
	bgColor= z1_to_hex( colorsys.hsv_to_rgb(hue,0.2,1) ) #A: hue al azar, poca saturacion, maximo brillo
	tpl= tpl.replace('fill:#afdde9',f'fill:#{bgColor}')
	#A: reemplace el color de fondo por uno al azar


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


class CharlaComoPathListView(CharlaListView): #U: la lista de charlas ej. t/sabado/cada_mes para buscar titulos que digan sabado y cada_mes
	def get_queryset(self):
		como_path= self.kwargs["un_path"]
		if not como_path is None:
			palabras= como_path.split('/') #A: una lista, separe usando /
			logger.debug(f'CharlaComoPathListView {palabras}')
			if len(palabras)>0: #A: al menos una palabra
				filtro= '%'+'%'.join(palabras)+'%'  #ej. %banda%django% 
				q= Charla.objects.filter(titulo__like=filtro).all()
				logger.debug(q.query)
				return q
		#A: si llegue aca es porque no habia filtros
		return Charla.objects.all()

# S: Charla vista comoda ##################################
def charla_texto_list(request, charla_titulo=None, pk=None): #U: los textos de UNA charla, btn para agregar
	if not pk is None:
		charla= get_object_or_404(Charla, pk=pk)
	else:
		charla= get_object_or_404(Charla, titulo= '#'+charla_titulo)

	fh_visita_anterior= datetime.date(1972,1,1) #DFLT: como si hubiera venido hace muchiiiisimo
	if request.user.is_authenticated:
		anteriores= Visita.objects.filter(de_quien= request.user, charla= charla)
		if len(anteriores)>0: #A: ya vino antes
			visita_anterior= anteriores.first()
			fh_visita_anterior= visita_anterior.fh_visita
			visita_anterior.delete() #A: quiero solo la ultima
		v= Visita(de_quien= request.user, charla= charla)
		v.save()
		#A: guarde que esta usuaria ya vio esta charlar hasta esta hora
	
	participantes= charla_participantes(charla_titulo= charla_titulo, charla_pk= pk).order_by('-fh_ultimo') #A: con menos adelante es descendiente, mas reciente arriba

	textos= charla.textos.order_by('fh_creado').all()
	return render(request, 'pa_charlas_app/texto_list.html', {'object_list': textos, 'participantes': participantes, 'charla': charla, 'titulo': charla.titulo, 'puede_crear': True, 'fh_visita_anterior': fh_visita_anterior })

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
