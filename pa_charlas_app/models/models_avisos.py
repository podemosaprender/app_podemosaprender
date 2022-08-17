from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User
from pa_charlas_app.models import BaseModel


class AvisoModel(BaseModel):
    """
    Aviso donde se publicaran los servicios que cada usuario ofrece, por ejemplo los seminarios.
    """
    class Meta:
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'

    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    detalle = models.TextField()
    precio = models.FloatField(help_text='Precio del aviso reflejado en PodemosTokens')

    def __str__(self):
        return f'{self.titulo} de {self.autor}, por ${self.precio}'