#INFO: tests locales (django crea db temporal)

from .util import BaseTextCase
from pa_charlas_app.models import *

#VER: https://docs.python.org/3/library/unittest.html#classes-and-functions
#VER: https://docs.python.org/3/library/unittest.html#assert-methods


class TextoGraphQLTest(BaseTextCase):
	def test_texto_crear(self):
		crear_res = self.queryComoParticipante(
			'''
				mutation pruebaTexto { 
							textoModificar(input: {texto: "otro va en #bandadjango"} ) { 
								clientMutationId texto { id texto fhCreado fhEditado } } 
				}
		  '''
		)

		buscar_res = self.queryComoParticipante(
			'''
				query pruebaTexto {
					textoLista { edges { node {id texto fhCreado fhEditado deQuien { username }} }}
				}	
			'''
		)
		#DBG: print(buscar_res)
		lista= buscar_res['data']['textoLista']['edges']
		self.assertEqual(len(lista),1)
		self.assertEqual(lista[0]['node']['deQuien']['username'], 'pepita')
		return buscar_res

	def test_texto_modificar(self):
		r0= self.test_texto_crear()
		lista0= r0['data']['textoLista']['edges']
		node0= lista0[0]['node']
		id0= node0['id']
		texto0= node0['texto']

		texto_modificado= "otro va en #bandadjango y lo modifique"
		modificar_res = self.queryComoParticipante(
			'''
				mutation pruebaTexto { 
							textoModificar(input: {texto: "'''+ texto_modificado+'''", id: "''' + id0 + '''"} ) { 
								clientMutationId texto { id texto fhCreado fhEditado } } 
				}
		 	'''
		)

		buscar_res = self.queryComoParticipante(
			'''
				query pruebaTexto {
					textoLista { edges { node {id texto fhCreado fhEditado deQuien { username }} }}
				}	
			'''
		)
		#DBG: print(buscar_res)

		lista1= buscar_res['data']['textoLista']['edges']
		node1= lista1[0]['node']
		id1= node1['id']
		texto1= node1['texto']

		self.assertEqual(len(lista1),1)		
		self.assertIn(texto_modificado, texto1)


	def test_texto_modificar_no_ajenos(self):
		r0= self.test_texto_crear()
		lista0= r0['data']['textoLista']['edges']
		node0= lista0[0]['node']
		id0= node0['id']
		texto0= node0['texto']
		user0= node0['deQuien']['username']
		fhEditado0= node0['fhEditado']

		self.assertEqual(user0,'pepita')

		texto_modificado= "otro va en #bandadjango y lo modifique como juancito"

		LanzoExcepcion= False
		try: 
			modificar_res = self.queryComoParticipante(
				'''
					mutation pruebaTexto { 
								textoModificar(input: {texto: "'''+ texto_modificado+'''", id: "''' + id0 + '''"} ) { 
									clientMutationId texto { id texto fhCreado fhEditado } } 
					}
				''',
				'juancito'	
			)
			print('MODIFICAR COMO juancito', modificar_res)	
		except Exception as ex:
			print('MODIFICAR COMO juancito EXCEPCION', ex)
			LanzoExcepcion= True

		self.assertEqual(LanzoExcepcion,True)

		buscar_res = self.queryComoParticipante(
			'''
				query pruebaTexto {
					textoLista { edges { node {id texto fhEditado fhCreado deQuien { username }} }}
				}	
			'''
		)
		print('MODIFICAR COMO juancito, buscando', buscar_res)
		lista1= buscar_res['data']['textoLista']['edges']
		node1= lista1[0]['node']
		id1= node1['id']
		texto1= node1['texto']
		user1= node1['deQuien']['username']
		fhEditado1= node1['fhEditado']

		self.assertEqual(len(lista1),1)		
		self.assertNotIn('juancito', texto1)
		self.assertEqual(texto0, texto1)
		self.assertEqual('pepita', user1)
		self.assertEqual(fhEditado1, fhEditado0)

