#INFO: com views pero para la API REST
#VER: https://www.django-rest-framework.org/api-guide/views/
#VER: https://www.django-rest-framework.org/api-guide/generic-views/#examples

from rest_framework import viewsets, mixins, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from django.shortcuts import get_list_or_404, get_object_or_404
import django
from rest_framework.permissions import IsAuthenticated

from .models import (
	Charla, CharlaItem, charla_tipo_tema, charla_participantes, 
	Texto, 
	User
)
from .serializers import *

from rest_framework.decorators import api_view

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def token_user(request, format=None):
    content = {
        'user': str(request.user),  # `django.contrib.auth.User` instance.
        'auth': (None if request.auth is None else 'yqwuyeuyqhhwhwh11hjhmirasitevoyadarmiclavejajaja'),  # None
    }
    return Response(content)

class TextoViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Texto.objects.all()
	serializer_class = TextoSerializer

class CharlaViewSet(viewsets.ViewSet):
	
	def list(self, request):
		queryset = Charla.objects.all()
		serializer = CharlaSerializer(queryset, many=True)
		return Response(serializer.data)

	def retrieve(self, request, pk=None):
		queryset = Charla.objects.all()
		charla = get_object_or_404(queryset, pk=pk)
		serializer = CharlaTextoSerializer(charla)
		return Response(serializer.data)

	#VER: https://www.django-rest-framework.org/api-guide/routers/ EXTRA ACTIONS
	@action(detail=True) #A: aparece en api/charla/1/participantes/
	def participantes(self, request, pk): 
		queryset= charla_participantes(charla_pk= pk)
		serializer= CharlaParticipanteSerializer(queryset, many= True)
		return Response(serializer.data)		

#VER: alternativa con permisions https://stackoverflow.com/a/54772675
class CharlaItemViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
	#A: solo permito las acciones de los mixins que liste Create, Destroy
	queryset = CharlaItem.objects.all()
	serializer_class = CharlaItemSerializer

	#VER: https://www.django-rest-framework.org/api-guide/generic-views/
	def perform_create(self, serializer):
		#DBG: print(serializer.validated_data)

		charla_titulo= serializer.validated_data.get('charla__titulo')
		texto_id= serializer.validated_data.get('texto__pk')
		#DBG: print(charla_titulo)
		#TODO: validar que sea un titulo aceptable

		charla_q= Charla.objects.filter(
			titulo= charla_titulo
		)
		if charla_q.exists():
			charla= charla_q.first() #A: existia, uso esa
		else: #A: no existia ninguna con ese titulo
			charla= Charla(
				titulo= charla_titulo,
				tipo= charla_tipo_tema(),
				de_quien= self.request.user
			)
			charla.save() #A: la cree y la guarde
			#TODO:SEC:no dejarme agregar textos a charlas de otro participante

		(item, loCreoP)= CharlaItem.objects.get_or_create(  #A: si estaba O crea me consigue el pk
			texto_id= texto_id,
			charla= charla
		)
		serializer.validated_data['pk']= item.pk #A: le paso el pk a la respuesta q va al navegador

	def perform_delete(self, serializer):
		CharlaItem.objects.filter(	
			charla__titulo= serializer.charla,
			texto= serializer.texto
		).delete() #A: si existe para ese dueño lo borra, sino no dice nada
			

class ParticipanteViewSet(viewsets.ReadOnlyModelViewSet):
	queryset= User.objects.all()
	serializer_class= UserSerializer
