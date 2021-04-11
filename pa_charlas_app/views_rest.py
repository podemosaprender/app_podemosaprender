#INFO: com views pero para la API REST
#VER: https://www.django-rest-framework.org/api-guide/views/
#VER: https://www.django-rest-framework.org/api-guide/generic-views/#examples

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .models import Charla, charla_participantes, Texto, User
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

class ParticipanteViewSet(viewsets.ReadOnlyModelViewSet):
	queryset= User.objects.all()
	serializer_class= UserSerializer
