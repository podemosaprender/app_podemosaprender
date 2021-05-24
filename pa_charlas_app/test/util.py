#INFO: para escribir mas facil los test

from graphene_django.utils.testing import GraphQLTestCase
from django.test import Client
import json

from pa_charlas_app.models import *

class BaseTextCase(GraphQLTestCase):
	def participanteCrear(self, username):
		(u, ignore)= User.objects.get_or_create(username=username, email=f'{username}@x.test')
		u.set_password(f'P{username}P')
		u.save()

	def participanteGetToken(self, username):
		otraApp= Client()
		res= otraApp.post(
			'/api/token/',
			data= {'username': username, 'password': f'P{username}P'}, 
			content_type='application/json',
			follow=True
		)
		#DBG: print(res.json())
		token= res.json().get('access')
		self.tokens= self.tokens if hasattr(self,'tokens') else {}
		self.tokens[username]= token
		return token

	def queryComoParticipante(self, q, username='pepita'):
		res= self.query(
			q,
			headers= {"HTTP_AUTHORIZATION": f"Bearer {self.tokens[username]}"}
		)
		self.assertResponseNoErrors(res)
		return json.loads(res.content)

	def setUp(self):
		for participante in ['pepita','juancito','maurito','anita']:
			self.participanteCrear(participante)
			self.participanteGetToken(participante)

