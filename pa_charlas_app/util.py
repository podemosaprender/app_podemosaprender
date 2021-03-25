import re

DiasNombre = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'] #A: Para python Lunes = 0
MesesNombre = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

def tag_fecha_a_calendario(tag): #U: Convierte el texto de un tag fecha a un diccionario manejable
	"""
	Patrones para los titulos de charla

	dia_
	dia_sabado_1ro_cada_mes
	dia_sabado_2do_cada_mes
	dia_sabado_1_antes_fin_de_mes
	dia_sabado_antes_fin_de_mes
	dia_sabado_de_enero

	dia_23_marzo_2021_13hs
	dia_lunes_a_viernes_19hs
	dia_lunes_miercoles_viernes_19hs

	dia_sabado_1ro_marzo
	dia_sabado_1ro_junio_julio
	dia_sabado_1ro_marzo_a_junio
	"""

	result = {'tipo': 'error', 'tag': tag} #DFLT
	partes = tag.split('_')
	if len(partes) > 0 and partes[0] == 'dia':
		en_que_dias = list(filter(lambda d: d in tag, DiasNombre))
		if len(en_que_dias) > 0:
			#EJ: dia_sabado_1_antes_fin_de_mes dia_sabado_antes_fin_de_mes
			#EJ: dia_sabado_1ro_marzo
			#EJ: dia_sabado_1ro_enero_a_marzo
			m = re.search(r'\d+', partes[2]) 
			numero = int(m.group(0)) if not m is None else 0
			en_que_meses = list(filter(lambda m: m in tag, MesesNombre))
			es_cada_mes = -1 if 'antes_fin_de_mes' in tag else 1 if len(en_que_meses) == 0 else 0

			if es_cada_mes == -1:
				numero = (numero + 1) * -1
				#EJ: dia_sabado_1_antes_fin_de_mes -> -2
				#EJ: dia_sabado_antes_fin_de_mes -> -1
			#A: Guardamos numero = 0 para los que se repiten todo el mes

			if len(en_que_meses) == 2 and '_a_'.join(en_que_meses) in tag:
				idx0 = MesesNombre.index(en_que_meses[0])
				idx1 = MesesNombre.index(en_que_meses[1])
				en_que_meses = MesesNombre[idx0:(idx1 + 1)]

			if len(en_que_dias) == 2 and '_a_'.join(en_que_dias) in tag:
				idx0 = DiasNombre.index(en_que_dias[0])
				idx1 = DiasNombre.index(en_que_dias[1])
				en_que_dias = DiasNombre[idx0:(idx1 + 1)]

			en_que_dias_num = list(map(DiasNombre.index, en_que_dias))
			en_que_meses_num = list(map(MesesNombre.index, en_que_meses))

			result = {'tipo': 'periodico', 'tag': tag, 'nro_en_mes':numero, 'en_que_dias': en_que_dias_num, 'en_que_meses': en_que_meses_num, 'es_cada_mes': es_cada_mes}
		else: #A: dia_23_marzo_2021 
			m = re.search(r'dia_(\d+)_([a-z]+)_(\d+)', tag)
			if not m is None and m.group(2) in MesesNombre:
				dia = int(m.group(1))
				mes = MesesNombre.index(m.group(2))
				anio = int(m.group(3))
				result = {'tipo': 'una_vez', 'tag': tag, 'dia': dia, 'mes': mes, 'anio': anio}
		
		m = re.search(r'(\d+)hs', tag)
		if not m is None:
			result['hora'] = m.group(1)

		#A: Si el formato es incorrecto tipo es 'error'

	return result
