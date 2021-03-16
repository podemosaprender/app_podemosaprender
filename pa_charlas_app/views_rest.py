#INFO: com views pero para la API REST
#VER: https://www.django-rest-framework.org/api-guide/views/
#VER: https://www.django-rest-framework.org/api-guide/generic-views/#examples

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response

from .models import Charla, Texto
from .serializers import CharlaSerializer, TextoSerializer

class CharlaViewSet(viewsets.ModelViewSet):
    queryset = Charla.objects.all()
    serializer_class = CharlaSerializer

class TextoViewSet(viewsets.ModelViewSet):
    queryset = Texto.objects.all()
    serializer_class = TextoSerializer

