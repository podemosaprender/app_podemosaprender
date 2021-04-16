#INFO: com views pero para la API REST
#VER: https://www.django-rest-framework.org/api-guide/views/
#VER: https://www.django-rest-framework.org/api-guide/generic-views/#examples

from rest_framework import viewsets, mixins, permissions, generics, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from django.shortcuts import get_list_or_404, get_object_or_404
import django
from rest_framework.permissions import IsAuthenticated

from .models import (
	Charla, CharlaItem, charla_tipo_tema, charla_participantes, charla_agregar_texto,
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
	permission_classes = [IsAuthenticated] #A: solo si puso usario y clave

	#VER: https://www.django-rest-framework.org/api-guide/generic-views/
	def perform_create(self, serializer):
		#DBG: print(serializer.validated_data)

		charla_titulo= serializer.validated_data.get('charla__titulo')
		texto_id= serializer.validated_data.get('texto__pk')
		orden= serializer.validated_data.get('orden') #A: es opcional

		#DBG: print(charla_titulo, texto_id)
		if not charla_agregar_texto(charla_titulo, texto_id, self.request.user, orden=orden):
			raise exceptions.ValidationError({'charla__titulo': f'"{charla_titulo} no es un título de charla valido'})
		
		#A: si salio todo bien, ya esta.
		

	def perform_delete(self, serializer):
		CharlaItem.objects.filter(	
			charla__titulo= serializer.charla,
			texto= serializer.texto
		).delete() #A: si existe para ese dueño lo borra, sino no dice nada
			

class ParticipanteViewSet(viewsets.ReadOnlyModelViewSet):
	queryset= User.objects.all()
	serializer_class= UserSerializer
