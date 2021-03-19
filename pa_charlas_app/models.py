from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone

from .models_extra import * #A: para que agregue otros lookups como like 

import logging
logger = logging.getLogger(__name__)

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

# S: funciones comodas ######################################
from .hashtags import hashtags_en
def conUserYFecha_guardar(form, user, commit= True):
	obj= form.save(commit=False)
	if not 'de_quien' in obj.__dict__ or obj.de_quien is None: #A: es nuevo
		obj.de_quien= user
		obj.fh_creado= timezone.now()
	elif obj.de_quien != user: #A: no era el autor!
		raise PermissionDenied	
	else:
		pass
	
	#A: no debe pasar de aca si no es el duño del objeto	
	if 'fh_editado' in obj.__dict__: 
		obj.fh_editado= timezone.now()
		logger.debug('set fh_editado')	
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

