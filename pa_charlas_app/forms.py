from django import forms

from .models import Texto, Imagen, AvisoModel

class TextoForm(forms.ModelForm):
	class Meta:
		model = Texto
		fields = ('texto',)

class ImagenForm(forms.ModelForm):
	class Meta:
		model = Imagen
		fields = ('imagen',)

class AvisoForm(forms.ModelForm):
	class Meta:
		model = AvisoModel
		exclude = ('autor',) #A: el autor lo voy a tomar del user logueado, no quiero que lo ingrese en el form
