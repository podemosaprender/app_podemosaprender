from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import re

from .models_extra import * #A: para que agregue otros lookups como like 

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

	def __str__(self):
		return f'{self.charla.titulo} {self.texto}'


class Visita(models.Model): #U: cuando vio por ultima vez cada charla una usuaria
	charla= models.ForeignKey('Charla', on_delete=models.CASCADE)
	de_quien= models.ForeignKey('auth.User', on_delete=models.CASCADE)
	fh_visita= models.DateTimeField(default=timezone.now)

	#TODO: asegurar que cada par (de_quien, charla) esta UNA sola vez. unique_together?

	def __str__(self):
		return f'{self.de_quien.username} {self.charla.titulo} {self.fh_visita}'

# S: funciones comodas ######################################
from .hashtags import hashtags_en
def conUserYFecha_guardar(form, user, commit= True):
	obj= form.save(commit=False)
	try:
		de_quien_vacio= (texto.de_quien is None) #A: si no es none, no lanza excepcion y guarda false
	except:
		de_quien_vacio= True
	if de_quien_vacio: #A: Si no tiene autor es nuevo 
		obj.de_quien= user
		obj.fh_creado= timezone.now() 
	elif obj.de_quien != user: #A: no era el autor!
		raise PermissionDenied	
	else:
		pass
	
	#A: no debe pasar de aca si no es el duño del objeto	
	if 'fh_editado' in obj.__dict__: 
		obj.fh_editado= timezone.now()
	#A: si tiene un field fh_editado lo actualizamos

	if commit:
		obj.save() #A: guarde el obj actualizado, para poder agregarlo a charlas
	return obj

def texto_guardar(form, user, charla_pk=None):
	texto= conUserYFecha_guardar(form,user,False) #A: no hago el save

	#TODO:SEC no dejar modificar textos de otro user
	if not charla_pk is None:
		ch= Charla.objects.get(pk= charla_pk)
		if not ch.titulo in texto.texto:
			texto.texto += f'\n{ch.titulo}'
		#A: si venia de una charla, le agrego el hashtag automaticamente
	else:
		hashtag= f'#casual{ timezone.now().strftime("%y%m%d%H%M") }{user.username}'
		if not hashtag in texto.texto:
			texto.texto += f'\n{hashtag}'
		#A: si no venia de una charla, empieza una casual

	hts= hashtags_en(texto.texto)
	logger.info(f'DB TEXTO {user.username} charla={charla_pk} hashtags={hts}')
	texto.save()


	#TODO:SEC: limitar quien y cuantas charlas puede crear, es facil crear muuchas
	tch_tema= TipoCharla.objects.get(titulo='Tema')

	CharlaItem.objects.filter(texto= texto.pk).delete() #A: borramos y volvemos a crear los tags
	#TODO: borrar las charlas que se hayan quedado sin items

	for ht in hts:
		chs= Charla.objects.filter(titulo= ht) 
		if chs.exists(): #A: la charla ya existia
			ch= chs.first() 
		else:
			ch= Charla(de_quien= user, titulo= ht, tipo= tch_tema)
			ch.de_quien= user
			ch.fh_creado= timezone.now()
			ch.save()	#A: cree una charla nueva, la guardo para poder agregar el texto

		ch.textos.add(texto)
		ch.save()

	return texto
# S: consultas comodas #####################################

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
