from django.db import models
from django.utils import timezone

class Texto(models.Model): #U: cualquier texto que publiquemos, despues especializamos
	de_quien= models.ForeignKey('auth.User', on_delete=models.CASCADE)
	fh_creado= models.DateTimeField(default=timezone.now)
	titulo= models.CharField(max_length=200)
	texto= models.TextField()

	def __str__(self):
		return f'{self.fh_creado} {self.de_quien} {self.titulo}'
