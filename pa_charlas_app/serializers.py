#INFO: generan json para la API REST
#VER: https://www.django-rest-framework.org/tutorial/1-serialization/#using-modelserializers

from rest_framework import serializers

from .models import Texto, Charla

class TextoSerializer(serializers.ModelSerializer):
	class Meta:
		model= Texto
		fields= ['pk','de_quien','fh_creado','fh_editado','texto']

#VER: (ManyToMany) https://www.django-rest-framework.org/api-guide/relations/
class CharlaSerializer(serializers.ModelSerializer):
	textos= TextoSerializer(many=True, read_only=True)
	class Meta:
		model= Charla
		fields= ['titulo','textos']
