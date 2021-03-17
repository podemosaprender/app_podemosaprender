#INFO: com views pero para la API REST
#VER: https://www.django-rest-framework.org/api-guide/views/
#VER: https://www.django-rest-framework.org/api-guide/generic-views/#examples

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404

from .models import Charla, Texto
from .serializers import CharlaSerializer, CharlaTextoSerializer, TextoSerializer

from rest_framework.decorators import api_view

class TextoViewSet(viewsets.ModelViewSet):
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

