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


class ContactForm(forms.Form):
    from_email = forms.EmailField(label="Email", required=True)
    subject = forms.CharField(label="Asunto", required=True)
    message = forms.CharField(label="Mensaje", widget=forms.Textarea, required=True)