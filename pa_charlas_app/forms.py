from django import forms

from .models import Texto, Imagen

class TextoForm(forms.ModelForm):
	class Meta:
		model = Texto
		fields = ('texto',)

class ImagenForm(forms.ModelForm):
	class Meta:
		model = Imagen
		fields = ('imagen',)
