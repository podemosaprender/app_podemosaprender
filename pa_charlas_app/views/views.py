#SEC: manejamos login_required en urls.py

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import View, ListView

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm
from django.contrib.auth import authenticate, login

from django.core.paginator import Paginator
from django import forms
import re
import os
import datetime as dt

from ..models import (
	Imagen,
	Texto, texto_guardar, textos_de_usuario,
	Charla, TipoCharla, Visita, charla_participantes, charlas_que_sigo, charlas_y_ultimo,
	usuario_para, redes_de_usuario,
	charlas_calendario
)
from ..forms import ImagenForm, TextoForm
from ..util import *

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
	redes = redes_de_usuario(request.user) if request.user.is_authenticated else {}
	#DBG: redes = {'facebook':12345, 'google':31}
	return render(request, 'pa_charlas_app/login.html', {'redes': redes})

from social_django.models import UserSocialAuth
import base64
import hashlib
import hmac
from django.conf import settings
from django import urls
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
@method_decorator(csrf_exempt, name='dispatch')
class FacebookDataDeletionView(View): #U: para eliminar datos como pide Facebook
	#VER: https://developers.facebook.com/docs/development/create-an-app/app-dashboard/data-deletion-callback/#implementing
	def post(self, request, *args, **kwargs): #U: facbook nos manda un post
		try:
			signed_request = request.POST['signed_request']
			print(f'FACEBOOK delete req {signed_request}')
			encoded_sig, payload = signed_request.split('.')
		except (ValueError, KeyError):
			return HttpResponse(status=400, content='Invalid request')

		try:
			decoded_payload = base64.urlsafe_b64decode(payload + "==").decode('utf-8')
			decoded_payload = json.loads(decoded_payload)

			if type(decoded_payload) is not dict or 'user_id' not in decoded_payload.keys():
				return HttpResponse(status=400, content='Invalid payload data')
		except (ValueError, json.JSONDecodeError):
			return HttpResponse(status=400, content='Could not decode payload')

		try:
			secret= settings.SOCIAL_AUTH_FACEBOOK_SECRET
			sig= base64.urlsafe_b64decode(encoded_sig + "==")
			expected_sig= hmac.new(bytes(secret, 'utf-8'), bytes(payload, 'utf-8'), hashlib.sha256)
		except:
			return HttpResponse(status=400, content='Could not decode signature')

		if not hmac.compare_digest(expected_sig.digest(), sig):
			return HttpResponse(status=400, content='Invalid request')

		user_id= decoded_payload['user_id'] #A: user_id segun facebook

		print(f'FACEBOOK DELETE user_id={user_id}')
		try:
			fb_user_account = UserSocialAuth.objects.get(uid=user_id, provider='facebook')
			fb_user_account.delete()
			logger.info(f'FACEBOOK DELETED {fb_user_account}')
		except FacebookLoginDetails.DoesNotExist:
			return HttpResponse(status=200)

		code= f'{timezone.now().toordinal():x}'
		response_data= {
			'url': request.build_absolute_uri( urls.reverse('facebook_delete_data_check', kwargs= {'code': code}) ),
			'confirmation_code': code,
		}
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

class FacebookDataDeletionCheckView(View): #U: para eliminar datos como pide Facebook
	def get(self, request, *args, **kwargs): #U: facbook nos manda un post
		return HttpResponse('Your data has been deleted', status=200)

def UserPassCambiar(request): #U: cambiar clave sin poner la anterior, ej. pq creaste cuenta con gmail
	if request.method == 'POST':
		form = SetPasswordForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return redirect('user_pass_cambiar')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = SetPasswordForm(request.user)
	return render(request, 'pa_charlas_app/user_pass_cambiar_form.html', { 'form': form })


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


#S: imagenes ##############################################

def imagen_edit(request, imagen_titulo=None): #U: crear Y editar textos, de charlas o para empezar una
	imagen= None #DFLT, nuevo
	error_a_responder= None #DFLT	
	if not imagen_titulo is None:
		if not re.match(r'^[a-zA-Z0-9_-]+$', imagen_titulo):
			error_a_responder= 'Nombre de imagen no válido'
		else:
			imagen_q = Imagen.objects.filter(titulo=imagen_titulo) #A: esta tratando de editar un imagen, puede no existir
			if imagen_q.exists():
				imagen= imagen_q.first() #A: si hay con ese titulo, la usamos
				if imagen.de_quien != request.user:
					#A: esta tratando de editar alguien que no tiene derechos
					error_a_responder= 'Sólo la persona que creo la imagen puede reemplazarla'

	if not error_a_responder is None:
		return redirect('/') #TODO: enviar mensaje de error 'no tiene permiso de editar este imagen'
	#A: tiene permisos y el titulo es valido

	if request.method == "POST":
		#VER: https://docs.djangoproject.com/en/3.2/topics/http/file-uploads/#handling-uploaded-files-with-a-model	
		form= ImagenForm(request.POST, request.FILES, instance= imagen)
		if form.is_valid():
			imagen= Imagen(titulo= imagen_titulo, de_quien= request.user) if imagen is None else imagen
			img_file= request.FILES['imagen']
			(x, ext)= os.path.splitext(img_file.name) #A: ext incluye el punto
			img_file.name= f'{imagen_titulo}{ext}' #A: le cambiamos el nombre, misma extension
			#TODO: race condition, si dos suben con el mismo nombre al mismo tiempo
			imagen.imagen= img_file 
			imagen.save()
			print(f'imagen_edit form valid {img_file.name}')
			return redirect('/') #TODO: cerrar la ventanita extra
		print(f'imagen_edit form NOT valid {form.errors} {request.FILES}')
	else:
		form = ImagenForm(instance= imagen)

	return render(
		request, 
		'pa_charlas_app/imagen_edit.html', 
		{
			'form': form, 
		})


#S: textos ################################################

def texto_edit(request, pk=None, charla_pk=None, charla_titulo=None): #U: crear Y editar textos, de charlas o para empezar una
	texto= None #DFLT, nuevo
	if not pk is None:
		texto= get_object_or_404(Texto, pk=pk) # A: esta tratando de editar un texto
		if texto.de_quien != request.user:
			#A: esta tratando de editar alguien que no tiene derechos
			return redirect('/') #TODO: enviar mensaje de error 'no tiene permiso de editar este texto'

	if request.method == "POST":
		form= TextoForm(request.POST, instance= texto)
		if form.is_valid():
			responde_charlaitem_pk = request.GET.get('responde') #A: charla item a la que estoy respondiendo o None
			print(f'texto_edit responde {responde_charlaitem_pk}')

			extra_data= enc_b64_o_r(request.POST.get('extra_form_data'),{})
			texto= texto_guardar(
				form, 
				texto.de_quien if texto else request.user, 
				charla_pk= extra_data.get('charla_pk'), 
				charla_titulo= extra_data.get('charla_titulo'), 
				responde_charlaitem_pk= responde_charlaitem_pk
			)

			#A: si no le pase una charla y no existia, crea una "casual"
			#A: si estoy editando un texto que ya tiene un autor que lo guarde con ese nombre, sino que use el del autor logueado
			logger.debug(f'VW texto {request.user.username} {extra_data}')
			return redirect(extra_data.get('volver_a') or '/')
	else:
		viene_de= request.META.get('HTTP_REFERER')
		form = TextoForm(instance= texto, initial={'viene_de': 'que_pasa'})
		extra_data= {'charla_pk': charla_pk, 'charla_titulo': charla_titulo, 'volver_a': viene_de}
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

def texto_list(request): #U: los textos de UNA charla, btn para agregar
	textos= Texto.objects.order_by('-fh_editado').all()
	paginator = Paginator(textos, 10) #A: ultimos 10
	page_number = request.GET.get('page',1)
	page_obj = paginator.get_page(page_number)
	return render(request, 'pa_charlas_app/texto_list.html', {'object_list': page_obj, 'titulo': 'Textos recientes'})

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

class CharlaQueSigoListView(ListView): #U: la lista de charlas que visite
	template_name= 'pa_charlas_app/charla_quesigo_list.html'
	paginate_by = 20  
	order_by='titulo'
	extra_context= {
		'type_name': 'charla',
		'type_url_base': 'charla',
		'create_url': '/charla/nueva',
		'titulo': 'Charlas',
		'vista_detalle': 'charla_texto_list_k',
	}

	def get_queryset(self):
		if self.request.user.is_authenticated:
			return charlas_que_sigo(self.request.user)	
		else:
			return charlas_y_ultimo()	

# S: Charla vista comoda ##################################
def charla_texto_list(request, charla_titulo=None, pk=None, prefijo_tag='#', orden='texto__fh_creado', mostrar_titulo= None): #U: los textos de UNA charla, btn para agregar, prefijo_tag puede ser @ para un usuario
	if not pk is None:
		charla_qs= Charla.objects.filter(pk=pk)
	else:
		charla_qs= Charla.objects.filter(titulo= prefijo_tag+charla_titulo)

	if charla_qs.exists():
		charla = charla_qs.first() 
	else:
		tch_tema= TipoCharla.objects.get(titulo='Tema')
		charla= Charla(titulo= prefijo_tag+charla_titulo, tipo= tch_tema, de_quien=request.user)
	#A: si la charla no existia, seguimos adelante con una temporal que NO queremos guardar


	if request.GET.get('o')=='reciente':
		orden='-texto__fh_editado'
	#DBG: print(request.GET.get('o'), orden)

	fh_visita_anterior= dt.date(1972,1,1) #DFLT: como si hubiera venido hace muchiiiisimo
	if request.user.is_authenticated and not charla.pk is None:
		anteriores= Visita.objects.filter(de_quien= request.user, charla= charla)
		if len(anteriores)>0: #A: ya vino antes
			visita_anterior= anteriores.first()
			fh_visita_anterior= visita_anterior.fh_visita
			visita_anterior.delete() #A: quiero solo la ultima
		v= Visita(de_quien= request.user, charla= charla)
		v.save()
		#A: guarde que esta usuaria ya vio esta charlar hasta esta hora
	
	participantes= charla_participantes(charla_titulo= charla_titulo, charla_pk= pk).order_by('-fh_ultimo') #A: con menos adelante es descendiente, mas reciente arriba

	charlaitems= charla.charlaitem_set.order_by('orden',orden).all() if not charla.pk is None else []

	paginator = Paginator(charlaitems, 50) 
	page_number = request.GET.get('page',1)
	page_obj = paginator.get_page(page_number)

	mostrar_titulo= charla.titulo if mostrar_titulo is None else mostrar_titulo
	return render(request, 'pa_charlas_app/charla_texto_list.html', {
		'object_list': page_obj, 
		'participantes': participantes, 
		'charla': charla, 
		'titulo': mostrar_titulo, 
		'puede_crear': True, 
		'fh_visita_anterior': fh_visita_anterior 
	})

# S: Usuarios ##############################################

def usuario_list(request):
	usuarios = User.objects.all()
	return render(request, 'pa_charlas_app/usuario_list.html',{'object_list': usuarios, 'titulo':'usuarios' })


def usuario_texto_list(request, username=None, pk=None): #U: los textos de UNA charla, btn para agregar
	user= usuario_para(request, username, pk)
	textos= textos_de_usuario(user).order_by('fh_creado').all()
	return render(request, 'pa_charlas_app/texto_list.html', {'object_list': textos, 'titulo': user.username})

def usuario_textos_que_nombran(request, username=None, pk=None): #U: como va un usuario respecto a su plan/intereses
	user= usuario_para(request, username, pk)
	return charla_texto_list(request, charla_titulo= user.username, prefijo_tag='@', orden='-fh_editado', mostrar_titulo=f'Textos que nombran a {user.username}')


def usuario_plan(request, username=None, pk=None): #U: como va un usuario respecto a su plan/intereses
	user= usuario_para(request, username, pk)

	charla_perfil= f'presentacion_de_participante_{user.username}' #U: si termina en de_participante_... solo escribe la dueña
	charla_plan= f'plan_de_participante_{user.username}' #U:  si termina en de_participante_... solo escribe la dueña

	charla_perfil_ideas= f'ayuda_presentacion_de_{user.username}' #U: le aportamos ideas
	charla_plan_ideas= f'ayuda_carrera_plan_{user.username}' #U: le aportamos ideas

	textosQueMeNombraron= Texto.objects.filter(charlaitem__charla__titulo='@'+user.username).order_by('-fh_editado').all()

	textosQueEscribi= textos_de_usuario(user).order_by('-fh_editado').all()

	textosPerfil= Texto.objects.filter(charlaitem__charla__titulo='#'+charla_perfil).order_by('fh_creado').all()
	textosPlan= Texto.objects.filter(charlaitem__charla__titulo='#'+charla_plan).order_by('fh_creado').all()

	textosPerfilIdeas= Texto.objects.filter(charlaitem__charla__titulo='#'+charla_perfil_ideas).order_by('-fh_editado').all()

	textosPlanIdeas= Texto.objects.filter(charlaitem__charla__titulo='#'+charla_plan_ideas).order_by('-fh_editado').all()

	return render(request, 'pa_charlas_app/usuario_plan.html', {
		'esteUsuario': user,
		'textosQueMeNombraron': textosQueMeNombraron,
		'textosQueEscribi': textosQueEscribi,

		'textosPerfil': textosPerfil,
		'charla_perfil': charla_perfil,
		'textosPerfilIdeas': textosPerfilIdeas,
		'charla_perfil_ideas': charla_perfil_ideas,

		'textosPlan': textosPlan,
		'charla_plan': charla_plan,
		'textosPlanIdeas': textosPlanIdeas,
		'charla_plan_ideas': charla_plan_ideas,
	})

# S: Calendario de eventos #################################

def evento_list(request): #U: lista de eventos proximos dias
	schedule, charla_a_eventos = charlas_calendario(31)
	
	return render(request, 'pa_charlas_app/evento_list.html', {'object_list': schedule, 'charla_a_eventos': charla_a_eventos, 'titulo': 'Próximos Eventos'})

def evento_list_ical(request): #U: idem evento_list pero en formato icalendar para importar eg en google, outlook
	from icalendar import Calendar, Event, vCalAddress, vText
	import pytz

	when_generated= timezone.now()

	cal = Calendar()
	cal.add('prodid', '-//PodemosAprender//mxm.dk//')
	cal.add('version', '2.0')

	organizer = vCalAddress('MAILTO:cal@podemosaprender.org')
	organizer.params['cn'] = vText('PodemosAprender')
	organizer.params['role'] = vText('APP')

	schedule, charla_a_eventos = charlas_calendario(31)
	#DBG: print('evento_list_ical', schedule, charla_a_eventos)
	for (when, charla) in schedule:
		#DBG: print('evento_list_ical', when, charla)
		for evento in charla_a_eventos.get(f'#{charla}',[]):
			event = Event()
			event['organizer'] = organizer
			event['uid'] = f'texto/{evento["id"]}/{when.strftime("%Y%m%d")}'
			#event['location'] = vText('Odense, Denmark')

			txt= re.sub(r'#casual\S+','',evento['texto'])
			if when.strftime('%H%M')=='0000': #A: no tiene horario
				hour= 9 #DFLT
				minute= 0	#DFLT
				m= re.search('(\d+)(:(\d+))?hs', txt)
				if not m is None:
					hour= int(m.group(1))
					minute= int(m.group(3)) if not m.group(3) is None else 0
				when= dt.datetime(when.year, when.month, when.day, hour, minute)
	
			#FALLA CON GOOGLE #when= pytz.utc.localize( when + dt.timedelta(hours=3) ) #A: pasamos de Arg=GMT-3 a UTC
			when= when + dt.timedelta(hours=3) #A: pasamos de Arg=GMT-3 a UTC

			event.add('summary', txt)
			event.add('dtstart', when)
			event.add('dtend', when+ dt.timedelta(hours=1))
			event.add('dtstamp', when_generated)
			event.add('priority', 5)

			cal.add_component(event)

	return HttpResponse( cal.to_ical(), content_type='text/calendar')

# S: Banco de horas #################################################################

def banco_list(request):
	return render(request,'pa_charlas_app/banco_horas.html',{'user':request.user})