import datetime as dt
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
			en_que_meses_num = list(map(lambda m: MesesNombre.index(m) + 1, en_que_meses))

			result = {'tipo': 'periodico', 'tag': tag, 'nro_en_mes':numero, 'en_que_dias': en_que_dias_num, 'en_que_meses': en_que_meses_num, 'es_cada_mes': es_cada_mes}
		else: #A: dia_23_marzo_2021 
			m = re.search(r'dia_(\d+)_([a-z]+)_(\d+)', tag)
			if not m is None and m.group(2) in MesesNombre:
				dia = int(m.group(1))
				mes = MesesNombre.index(m.group(2)) + 1
				anio = int(m.group(3))
				result = {'tipo': 'una_vez', 'tag': tag, 'dia': dia, 'mes': mes, 'anio': anio}
		
		m = re.search(r'(\d+)hs', tag)
		if not m is None:
			result['hora'] = int(m.group(1))

		#A: Si el formato es incorrecto tipo es 'error'

	return result

def primero_del_mes(dia_semana, mes, anio):
	if mes > 12:
		anio += mes // 12
		mes = ((mes - 1) % 12) + 1
	dia_1 = dt.datetime(anio, mes, 1)
	dia_semana_1 = dia_1.weekday()
	delta = dia_semana - dia_semana_1 + (7 if dia_semana_1 > dia_semana else 0)
	dia = dt.datetime(anio, mes, 1 + delta)
	return dia

def fechas_generadores_para(tag, fecha_min, semanas_max):
	generadores = []
	dia_desde = fecha_min.day
	mes_desde = fecha_min.month
	anio_desde = fecha_min.year
	d = tag_fecha_a_calendario(tag)
	if d['tipo'] == 'una_vez':
		if 'hora' in d:
			fecha = dt.datetime(d['anio'], d['mes'], d['dia'], d['hora'])
		else:
			fecha = dt.datetime(d['anio'], d['mes'], d['dia'])
		if (fecha >= fecha_min):
			generadores.append([(fecha, d)])
	elif d['tipo'] == 'periodico':
		if d['es_cada_mes'] != 0:
			nro_en_mes = d['nro_en_mes']
			dia_1 = dt.datetime(anio_desde, mes_desde, 1)
			dia_semana_1 = dia_1.weekday()
			for dia_semana in d['en_que_dias']:
				if nro_en_mes == 0: #A: Se repite todas las semanas
					dia_0 = primero_del_mes(dia_semana, mes_desde, anio_desde)
					generadores.append([
						(dia_0 + dt.timedelta(days = i * 7), d)
						for i in range(semanas_max)
					])
				elif nro_en_mes > 0: #A: cada_mes
					generadores.append([
						(primero_del_mes(dia_semana, mes_desde + i, anio_desde) + dt.timedelta(days = (nro_en_mes - 1) * 7), d)
						for i in range(semanas_max)
					])
				elif nro_en_mes < 0:
					generadores.append([
						(primero_del_mes(dia_semana, mes_desde + 1 + i, anio_desde) + dt.timedelta(days = nro_en_mes * 7), d) #A: nro_en_mes < 0 y pedi primer dia_semana del mes siguiente, => -1 ultimo de este mes
						for i in range(semanas_max)
					])
		elif d['es_cada_mes'] == 0:
			nro_en_mes = d['nro_en_mes']
			for mes in d['en_que_meses']:
				for dia_semana in d['en_que_dias']:
					if nro_en_mes == 0: #A: Todos del mes
						generadores.append([
							(fecha, d)
							for i in range(semanas_max)
							for fecha in [primero_del_mes(dia_semana, mes, anio_desde) + dt.timedelta(days = 7 * i)]
							if fecha.month == mes #A: No me sali de este mes
						])
					elif nro_en_mes > 0: #A: Alguno especifico del mes
						generadores.append([
							(primero_del_mes(dia_semana, mes, anio_desde + i) + dt.timedelta(days = (nro_en_mes - 1) * 7), d)
							for i in range(2) #A: Lo calculo para este anio y el siguiente
						])

	return generadores

def tags_a_schedule(tags, fecha_min, fecha_max):
	semanas_max = (fecha_max - fecha_min).days // 7 + 8 #A: Por si el primero del mes es el mes siguiente

	fechas = [
		(fecha[0], fecha[1]['tag'])
		for l in tags
		for generador in fechas_generadores_para(l, fecha_min, semanas_max)
		for fecha in generador
	]

	schedule = sorted(filter(lambda fecha: fecha_min <= fecha[0] and fecha[0] <= fecha_max, fechas))

	return schedule

