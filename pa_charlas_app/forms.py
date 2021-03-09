from django import forms

from .models import Texto

class TextoForm(forms.ModelForm):
	class Meta:
		model = Texto
		fields = ('texto',)
