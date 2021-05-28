from django.db import models
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone

from .models_charlas import User


class BancoTx(models.Model): # U: Una transaccion de horas entre dos usuarios
	
	quien_da= models.ForeignKey('auth.User',related_name="bancotx_da", on_delete=models.CASCADE)
	quien_recibe= models.ForeignKey('auth.User',related_name="bancotx_recibe" ,on_delete=models.CASCADE)
	quien_hace = models.ForeignKey('auth.User',related_name="bancotx_hace" ,on_delete=models.CASCADE, default=None)
	fh_creado= models.DateTimeField(default=timezone.now)
	titulo= models.CharField(max_length=200)
	cuanto= models.IntegerField()
	que = models.CharField(max_length=200) #A: Ejemplo de que: "horas de consultoria de Mauri"

	def __str__(self):
		return f'{self.fh_creado} {self.quien_da} {self.quien_recibe} {self.quien_hace} {self.cuanto} {self.titulo} '

# S: funciones del Banco de Horas #############################################

def hs_prometidas_detalle(user): #U: para saber si Alexander prometio varias reencarnaciones (20000000 horas)
    #TODO: descontar las que ya cumplio
    #VER: https://docs.djangoproject.com/en/3.2/topics/db/aggregation/#cheat-sheet
    prometidas = BancoTx.objects.filter(quien_hace=user, quien_da=user).aggregate(Sum('cuanto'))['cuanto__sum'] or 0
    cumplidas = BancoTx.objects.filter(quien_hace=user, quien_recibe=user).aggregate(Sum('cuanto'))['cuanto__sum'] or 0
    #A: cuando alguien cumple las horas, el que las tenia se las transfiere y queda quien_recibe = quien_hace
    saldo = prometidas - cumplidas
    return (saldo, prometidas, cumplidas)

def hs_prometidas(user):
    (saldo, prometidas, cumplidas) = hs_prometidas_detalle(user)
    return saldo

def hs_recibidas(user, que): #U: OJO! no descuenta las que ya gasto.
    hs_recibidas = BancoTx.objects.filter(quien_recibe=user, que=que).aggregate(Sum('cuanto'))['cuanto__sum'] or 0
    return hs_recibidas

def hs_para_usar_detalle(user, que):
    recibidas = hs_recibidas(user, que)
    #A: contamos las horas que recibio antes, el que ahora las va a dar

    horas_gastadas = BancoTx.objects.filter(quien_da=user, que=que).aggregate(Sum('cuanto'))['cuanto__sum'] or 0
    #A: tenemos que descontar las que ya entrego
    saldo = recibidas - horas_gastadas

    return (saldo, recibidas, horas_gastadas)


def hs_para_usar(user, que):
    (saldo, recibidas, horas_gastadas) = hs_para_usar_detalle(user, que)
    return saldo

#VER: https://docs.djangoproject.com/en/3.2/topics/db/transactions/#controlling-transactions-explicitly
@transaction.atomic #A: asegurar la consistencia de la operacion. Si lanza excepcion no se guarda nada.
def banco_registrar(quien_da, quien_recibe, cuanto, que="horas", quien_hace=None, titulo=None):
    #TODO: Averiguar de una forma segura si son propias
    #OJO: cuanto no puede ser negativo! 
    #TODO: quien_da solo debe el usuario activo.
    #TODO: podria tener fecha de expiracion
    #TODO: podria tener una condicion ejecutable (url tipo smart contract)
    #TODO: limite maximo de horas prometidos por usuario

    quien_hace = quien_da if quien_hace is None else quien_hace

    tx1 = BancoTx(
            quien_da=quien_da, 
            quien_recibe=quien_recibe, 
            quien_hace= quien_hace,
            titulo=titulo, 
            cuanto=cuanto, 
            que=que
        )
    if(tx1.cuanto<=0):
        #VER: https://docs.python.org/3/library/exceptions.html#ValueError
        raise ValueError('Cuanto debe ser positivo')
    tx1.save()

    if quien_da != quien_hace:   
        (horas_disponible, horas_recibidas, horas_gastadas) = hs_para_usar_detalle(quien_da, que)

        if horas_recibidas<horas_gastadas:
            raise ValueError(f'saldo insuficiente {horas_recibidas} < {horas_gastadas}')

    return tx1
    
def banco_registrar_UI(quien_da, quien_recibe, cuanto, que="horas", quien_hace=None, titulo=None):
    quien_da_user = User.objects.get(username=quien_da)
    quien_recibe_user = User.objects.get(username=quien_recibe)
    quien_hace_user = User.objects.get(username=quien_hace)

    return banco_registrar(quien_da_user, quien_recibe_user, cuanto, que, quien_hace_user, titulo)
