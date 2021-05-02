from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect

from .models_extra import * #A: para que agregue otros lookups como like 
from .util import *

import datetime as dt
import re
import hashlib

import logging
logger = logging.getLogger(__name__)

User= get_user_model() #U: la implementacion q este configurada

class Texto(models.Model): #U: cualquier texto que publiquemos, despues especializamos
	de_quien= models.ForeignKey('auth.User', on_delete=models.CASCADE)
	fh_creado= models.DateTimeField(default=timezone.now)
	fh_editado= models.DateTimeField(default=timezone.now)

	titulo= models.CharField(max_length=200)
	texto= models.TextField()

	def __str__(self):
		return f'{self.fh_creado} {self.de_quien} {self.titulo}'

class TipoCharla(models.Model): #U: casual, curso, etc.
	titulo= models.CharField(max_length=200, unique=True)

	def __str__(self):
		return self.titulo

class Charla(models.Model): #U: una coleccion de textos sobre algun tema
	de_quien= models.ForeignKey('auth.User', on_delete=models.CASCADE)
	fh_creado= models.DateTimeField(default=timezone.now)

	titulo= models.CharField(max_length=200, unique=True)

	tipo= models.ForeignKey('TipoCharla', on_delete=models.SET_DEFAULT, default=-1)
	textos= models.ManyToManyField(Texto, through='CharlaItem')

	def __str__(self):
		return f'{self.titulo} {self.tipo} {self.fh_creado} {self.de_quien} '

class CharlaItem(models.Model): #U: conecta un texto con una charla
	charla= models.ForeignKey('Charla', on_delete=models.CASCADE)
	texto=  models.ForeignKey('Texto', on_delete=models.CASCADE)
	orden= models.CharField(max_length=50, default='') #U: ordenamos 1ro por esto, despues por fecha
	nivel= models.IntegerField(default=0) #U: 0 es el de siempre, 1 es mas adentro ej. respuesta, 2 es comentario en la respuesta como un hilo en FB, etc.
	

	def __str__(self):
		return f'{self.charla.titulo} {self.texto}'

class Voto(models.Model): #U: una coleccion de textos sobre algun tema
	titulo= models.CharField(max_length=200, unique=True)

	def __str__(self):
		return f'{self.titulo}'

class VotoItem(models.Model): #U: conecta un texto con una charla
	de_quien= models.ForeignKey('auth.User', on_delete=models.CASCADE)
	texto=  models.ForeignKey('Texto', on_delete=models.CASCADE)
	voto= models.ForeignKey('Voto', on_delete=models.CASCADE)
	fh_creado= models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together= [["de_quien","texto" ,"voto"]]
		#A: asegurar que cada terna (de_quien, texto, voto) esta UNA sola vez.

	def __str__(self):
		return f'{self.voto.titulo} {self.de_quien} {self.texto}'

class Visita(models.Model): #U: cuando vio por ultima vez cada charla una usuaria
	charla= models.ForeignKey('Charla', on_delete=models.CASCADE)
	de_quien= models.ForeignKey('auth.User', on_delete=models.CASCADE)
	fh_visita= models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together= [["charla", "de_quien"]]
		#A: asegurar que cada par (de_quien, charla) esta UNA sola vez.

	def __str__(self):
		return f'{self.de_quien.username} {self.charla.titulo} {self.fh_visita}'

# S: funciones comodas ######################################
from .hashtags import hashtags_en
def charla_tipo_tema(): #U: por comodidad
	return TipoCharla.objects.get(titulo='Tema')

def conUserYFecha_guardar(form, user, commit= True):
	ahora= timezone.now() 
	obj= form.save(commit=False)
	try:
		de_quien_vacio= (texto.de_quien is None) #A: si no es none, no lanza excepcion y guarda false
	except:
		de_quien_vacio= True
	if de_quien_vacio: #A: Si no tiene autor es nuevo 
		obj.de_quien= user
		obj.fh_creado= ahora
	elif obj.de_quien != user: #A: no era el autor!
		raise PermissionDenied	
	else:
		pass
	
	#A: no debe pasar de aca si no es el duño del objeto	
	if 'fh_editado' in obj.__dict__: 
		obj.fh_editado= ahora
	#A: si tiene un field fh_editado lo actualizamos

	if commit:
		obj.save() #A: guarde el obj actualizado, para poder agregarlo a charlas
	return obj

def charla_titulo_valido(un_string): #U: devuelve un titulo de charla aceptado O None si no tiene arreglo
	if not un_string[0] in '@#':
		un_string= '#'+un_string
	hts= list(hashtags_en(f' {un_string} ', quiere_sin_tildes= False)) #A: nuestras urls y db soportan tildes
	#TODO: mover a hashtags_en , pq por ej. ahora requiere espacios alrededor del titulo y hay que hacer esta chanchada
	print(f'charla_titulo_valido "{un_string}" {hts}')
	if len(hts)>0 and hts[0] == un_string:
		return un_string
	else:
		return None

def charla_agregar_texto(charla_titulo, texto, user, orden= None, charla_tipo= None, nivel = None): #U: agrega el texto a la charla, q crea si es necesario
	puedeModificarEstaCharla= True #DFLT

	charla_titulo= charla_titulo_valido(charla_titulo)
	if charla_titulo is None:
		return False

	m= re.match(r'.*?de_participante_(.*)$',charla_titulo)
	if not m is None: #A: es una charla que solo puede modificar una participante
		puedeModificarEstaCharla= (m.groups(1)[0]	== user.username)

	if puedeModificarEstaCharla:
		chs= Charla.objects.filter(titulo= charla_titulo) 
		if chs.exists(): #A: la charla ya existia
			ch= chs.first() 
		else:
			charla_tipo= charla_tipo_tema() if charla_tipo is None else charla_tipo
			ch= Charla(de_quien= user, titulo= charla_titulo, tipo= charla_tipo)
			ch.de_quien= user
			ch.fh_creado= timezone.now()
			ch.save()	#A: cree una charla nueva, la guardo para poder agregar el texto

	
		texto_id= texto if type(texto)==int else texto.pk
		#DBG: print(f'TEXTO_ID {texto_id} CHARLA {ch}')
		(chit, loCreoP)= CharlaItem.objects.get_or_create(
			charla= ch,
			texto_id= texto_id
		)
		if not orden is None: #A: me pasaron un orden ej en una respuesta
			chit.orden= orden
		elif chit.orden is None: #A: no me pasaron Y no tenia puesto a mano de antes
			chit.orden= texto.fh_creado.strftime('_%y%m%d%H%M%S')

		if not nivel is None:
			chit.nivel= nivel

		chit.save()

		return True

	return False

def texto_guardar(form, user, charla_pk=None, charla_titulo=None, responde_charlaitem_pk= None):
	texto= conUserYFecha_guardar(form,user,False) #A: no hago el save
	#TODO: OjO! Si hay problema con las charlas, el texto se guarda igual. Que hacemos?

	#TODO:SEC no dejar modificar textos de otro user
	if charla_titulo is None and not charla_pk is None:
		ch= Charla.objects.get(pk= charla_pk)
		charla_titulo= ch.titulo

	nivel = 0 #DFTL
	orden = None #DFLT

	if not responde_charlaitem_pk is None:
		charlaitem_respondido = CharlaItem.objects.get(pk= responde_charlaitem_pk)
		nivel = charlaitem_respondido.nivel +1
		orden = charlaitem_respondido.orden + '-1'
		#A: si responde charla_titulo es el de la charla donde estoy respondiendo

	if not charla_titulo is None:	
		if not charla_titulo in texto.texto:
			texto.texto += f'\n\n {charla_titulo}'
		#A: si venia de una charla, le agrego el hashtag automaticamente, espacio para q no sea titulo markdown
	else:
		hashtag= f'#casual{ timezone.now().strftime("%y%m%d%H%M") }{user.username}'
		if not hashtag in texto.texto:
			texto.texto += f'\n\n {hashtag}' 
		#A: si no venia de una charla, empieza una casual, espacio para q no sea titulo markdown

	hts= hashtags_en(texto.texto, quiere_sin_tildes= False) #A: nuestras urls y db soportan tildes
	#DBG: print(f'hashtags {hts} en {texto.texto}')
	if '#juntada_virtual' in hts:
		if 'meet' in texto.texto or 'zoom' in texto.texto or 'jit' in texto.texto:
			pass #A: ya habla de algun servicio de conferencias
		else:
			mhash= hashlib.md5(f'{texto.pk} {texto.de_quien.username} {texto.fh_creado}'.encode('utf-8')).hexdigest()
			#A: un hash para que no se nos metan en la call adivinando PERO que no cambie despues que cree el texto
			tt= charla_titulo[1:] if not charla_titulo is None else texto.de_quien.username
			jitsi_link= f'https://meet.jit.si/pa_{tt}_{mhash}'
			texto.texto= texto.texto.replace('#juntada_virtual', f'#juntada_virtual [en este link]({jitsi_link})')
	logger.info(f'DB TEXTO {user.username} charla={charla_pk} hashtags={hts}')
	texto.save()


	#TODO:SEC: limitar quien y cuantas charlas puede crear, es facil crear muuchas
	tch_tema= charla_tipo_tema()

	CharlaItem.objects.filter(texto= texto.pk).exclude(charla__titulo__in=hts).delete() 
	#A: borramos de las charlas donde YA NO ESTA usando exclude con las que si

	#TODO: borrar las charlas que se hayan quedado sin items

	for ht in hts:
		if ht == charla_titulo:
			charla_agregar_texto(ht, texto, user, charla_tipo= tch_tema,orden=orden , nivel = nivel)
		else:
			charla_agregar_texto(ht, texto, user, charla_tipo= tch_tema)
		#A: charla_agregar_texto usa get_or_create para agregar o actualizar
			

	return texto

# S: consultas comodas #####################################
def usuario_para(request, username=None, pk=None): #U: conseguir con username, pk, o request
	if not pk is None:
		user= get_object_or_404(User, pk=pk)
	elif not username is None:
		user= get_object_or_404(User, username= username)
	else:
		user= request.user
	return user

def charla_participantes(charla_titulo= None, charla_pk= None): #U: participantes de una charla
	#VER: https://docs.djangoproject.com/en/3.1/topics/db/aggregation/
	q= ( #U: puedo ir guardando la consulta de a pasos, para componer o debug
		CharlaItem.objects #A: empiezo con todos los CharlaItem
		.select_related('de_quien__username') #A: aviso que voy a querer el username, asi no hace una consulta aparte por cada uno (lentisimo!)
	)

	if not charla_pk is None: #A: pidio filtrar las charlas por clave
		q= q.filter(charla__pk= charla_pk) 
	elif not charla_titulo is None: #A: filtro las charlas por clave
		q= q.filter(charla__titulo= charla_titulo) 
	else: #A: no paso ningun parametro para filtrar
		raise ObjectDoesNotExist #A: si no paso ningun filtro, lanzo una excepcion
		
	q= (
		q
		.values('texto__de_quien','texto__de_quien__username') #A: quiero agrupar por el id y username
		.annotate(fh_ultimo= models.Max('texto__fh_editado')) #A: y traer solo la fecha maxima
	)

	#DBG: print('charla_participantes', q.query) 
	return q.all()

def charlas_y_ultimo():
	qc= (
		Charla.objects
		.values('pk','titulo')
		.annotate(fh_ultimo= models.Max('textos__fh_editado'))
	)
	return qc

def charlas_que_sigo(user):
	qc= (
		Charla.objects
		.filter(visita__de_quien= user) 
		.values('pk','titulo','visita__fh_visita')
		.annotate(fh_ultimo= models.Max('textos__fh_editado'))
	)
	return qc	

def charlas_calendario(dias_max = 1): #U: Todas las charlas programadas entre hoy y hoy+dias_max, devuelve (fecha, tag)
	hoy_local = (dt.datetime.today() - dt.timedelta(hours=3)) #A: en hora de Arg TODO: usar locale compu
	fecha_min = dt.datetime(hoy_local.year, hoy_local.month, hoy_local.day) #A: desde las 00:00
	fecha_max = fecha_min + dt.timedelta(days = dias_max)

	todas_las_charlas = Charla.objects.filter(titulo__startswith = '#dia_')
	todos_los_eventos = (
		Texto.objects
		.filter(charlaitem__charla__id__in = todas_las_charlas)
		.values('charlaitem__charla_id', 'charlaitem__charla__titulo', 'id', 'texto')
		.order_by('charlaitem__charla__titulo')
	)
	charla_a_evento = {}
	for evento in todos_los_eventos:
		titulo = evento['charlaitem__charla__titulo']
		a = charla_a_evento.get(titulo, [])
		a.append(evento)
		charla_a_evento[titulo] = a

	todos_los_tags = [charla.titulo[1:] for charla in todas_las_charlas] #A: Saco el # del principio

	schedule = tags_a_schedule(todos_los_tags, fecha_min, fecha_max)

	return (schedule, charla_a_evento)

def textos_de_usuario(user): #U: Trae todos los textos hechos por une user
	q = (
		Texto.objects
		.filter(de_quien = user)
	)
	return q

def redes_de_usuario(user): #U: Diccionario red -> usr_id
	r = {}
	for red in user.social_auth.all():
		provider = re.sub(r'-.*', '', red.provider) #A: google-oatuh -> google
		r[provider] = red.uid
	return r
