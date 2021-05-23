#INFO: testear como un texto genera charlas, permisos, etc.

from .util import BaseTextCase
from pa_charlas_app.models import *
from pa_charlas_app.hashtags import hashtags_en
from pa_charlas_app.forms import TextoForm
from django.utils import timezone

#VER: models def texto_guardar(form, user, charla_pk=None, charla_titulo=None, responde_charlaitem_pk= None, orden=None):

class TextoComoInterpreteTest(BaseTextCase):
	def test_si_texto_nombra_charla_sola(self):
		elHashtag= 	'#UnHashtagSimple'
		textoDePrueba= f' {elHashtag} ' #ToDo: sin espacios no detecta el hashtag
		hts= list(hashtags_en(textoDePrueba, quiere_sin_tildes= False)) #A: nuestras urls y db soportan tildes
		self.assertEqual(hts,[elHashtag])

	def test_si_texto_nombra_charla_repetida_queda_una_sola(self):
		elHashtag= 	'#UnHashtagSimple'
		textoDePrueba= f' {elHashtag} {elHashtag} {elHashtag} {elHashtag} ' #ToDo: sin espacios no detecta el hashtag
		hts= list(hashtags_en(textoDePrueba, quiere_sin_tildes= False)) #A: nuestras urls y db soportan tildes
		self.assertEqual(hts,[elHashtag])

	def test_si_texto_nombra_charla_crea_y_agrega(self):
		participanteDePrueba= User.objects.get(username='pepita')

		charlaCasualEsperada= hastagCasual(participanteDePrueba); #U: la que agrega texto_guardar

		textoDePruba= 'esto va en #borrame_interpretar'
		textoForm= TextoForm({'texto': textoDePruba})
		if not textoForm.is_valid():
			raise ValidationError(textoForm.errors)

		item= texto_guardar(textoForm, participanteDePrueba)

		charlas= CharlaItem.objects.filter(texto_id= item.pk)
		self.assertEqual(charlas.filter(charla__titulo='#borrame_interpretar').exists(), True)

		otrasCharlas= charlas.exclude(charla__titulo='#borrame_interpretar')
		print(otrasCharlas)
		self.assertEqual(len(otrasCharlas), 1)
		self.assertEqual(otrasCharlas[0].charla.titulo, charlaCasualEsperada)

		self.assertIn(charlaCasualEsperada, item.texto) #A: el hashtag casual se incluye en el texto
		
		
