#INFO: generan json para la API REST
#VER: https://www.django-rest-framework.org/tutorial/1-serialization/#using-modelserializers

from rest_framework import serializers
from django.contrib.auth import get_user_model 

from .models import Texto, Charla, CharlaItem, VotoItem
User= get_user_model()

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model= User
		fields= ['username', 'pk']

class TextoSerializer(serializers.ModelSerializer):
	de_quien=UserSerializer(read_only=True)
	class Meta:
		model= Texto
		fields= ['pk','de_quien','fh_creado','fh_editado','texto']

#VER: (ManyToMany) https://www.django-rest-framework.org/api-guide/relations/
class CharlaTextoSerializer(serializers.ModelSerializer):
	textos= TextoSerializer(many=True, read_only=True)
	class Meta:
		model= Charla
		fields= ['titulo', 'pk', 'textos']

class CharlaSerializer(serializers.ModelSerializer):
	class Meta:
		model= Charla
		fields= ['titulo', 'pk']

class CharlaParticipanteSerializer(serializers.Serializer):
	#VER: https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
	user_pk= serializers.IntegerField(source='texto__de_quien')
	username= serializers.CharField(source='texto__de_quien__username')
	fh_ultimo= serializers.DateTimeField()

class CharlaItemSerializer(serializers.Serializer):
	charla_titulo= serializers.CharField(source='charla__titulo')
	texto_pk= serializers.CharField(source='texto__pk')	
	orden= serializers.CharField(required=False)	

class VotoItemSerializer(serializers.ModelSerializer):
	de_quien=UserSerializer(read_only=True)

	class Meta:
		model= VotoItem
		fields= ['pk','de_quien','fh_creado','texto' ,'voto']
		read_only_fields= ['pk','de_quien','fh_creado']

