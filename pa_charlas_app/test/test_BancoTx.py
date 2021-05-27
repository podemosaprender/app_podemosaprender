#INFO: testear el correcto funcionamiento del banquito de horas.

from .util import BaseTextCase
from pa_charlas_app.models import *
from django.db.models import Sum
from django.db import transaction

# Caso1: A anota que le debe 4 horas a M (M lo puede ver, no se puede cambiar. Esas horas solo las puede transferir o gastar M)
# Caso2: Sabemos cuantas horas A tiene prometidas a otras personas.
# Caso3: M le transfiere dos horas de A a X.
#   1. que M las tenga. 
#   2. que no quede en negativo
# Caso4: X confirma que A ya no le debe las horas.

# Ejemplo de que: "horas de consultoria de Mauri"

#VER: https://docs.djangoproject.com/en/3.2/topics/db/transactions/#controlling-transactions-explicitly
@transaction.atomic #A: asegurar la consistencia de la operacion 
def banco_registrar(quien_da, quien_recibe, cuanto, que="horas", titulo=None, son_propias= True):
    #TODO: Averiguar de una forma segura si son propias
    #TODO: cuanto no puede ser negativo!
    #TODO: quien_da solo debe el usuario activo.
    #TODO: podria tener fecha de expiracion
    #TODO: podria tener una condicion ejecutable (url tipo smart contract)
    #TODO: limite maximo de horas prometidos por usuario

    tx1 = BancoTx(
            quien_da=quien_da, 
            quien_recibe=quien_recibe, 
            titulo=titulo, 
            cuanto=cuanto, 
            que=que
        )
    if(tx1.cuanto<=0):
        #VER: https://docs.python.org/3/library/exceptions.html#ValueError
        raise ValueError('Cuanto debe ser positivo')
    tx1.save()

    if not son_propias:   
        horas_recibidas = BancoTx.objects.filter(quien_recibe=quien_da, que=que).aggregate(Sum('cuanto'))['cuanto__sum'] or 0
        #A: contamos las horas que recibio antes, el que ahora las va a dar

        horas_gastadas = BancoTx.objects.filter(quien_da=quien_da, que=que).aggregate(Sum('cuanto'))['cuanto__sum'] or 0
        #A: tenemos que descontar las que ya entrego

        if horas_recibidas<horas_gastadas:
            raise ValueError(f'saldo insuficiente {horas_recibidas} < {horas_gastadas}')

def horas_prometidas(user):
    #VER: https://docs.djangoproject.com/en/3.2/topics/db/aggregation/#cheat-sheet
    horas = BancoTx.objects.filter(quien_da=user).aggregate(Sum('cuanto'))
    return horas['cuanto__sum']

def horas_recibidas(user, que):
    horas_recibidas = BancoTx.objects.filter(quien_recibe=user, que=que).aggregate(Sum('cuanto'))['cuanto__sum']
    return horas_recibidas


userA = User.objects.get(pk=1)
userM = User.objects.get(pk=2)
userX = User.objects.get(pk=3)

class BancoTxTest(BaseTextCase):
    def test_crear_transaccion(self):

        
        banco_registrar(
            quien_da=userA, 
            quien_recibe=userM, 
            titulo="transaccion de prueba", 
            cuanto=10, 
            que="Horas de A para programar"
        )

        encontrado = BancoTx.objects.filter(
            quien_da=userA, 
            quien_recibe=userM, 
            titulo="transaccion de prueba", 
            cuanto=10, 
            que="Horas de A para programar"
        )
        self.assertEqual(encontrado.exists(),True)

    def test_cuanto_no_negativo(self):
        with self.assertRaises(ValueError):
            banco_registrar(
                quien_da=userA, 
                quien_recibe=userM, 
                titulo="no guardar cuanto negativo!", 
                cuanto=-1, 
                que="enseñar banda django"
            )
        
        encontrado = BancoTx.objects.filter(
            cuanto__lt=0, #A: lt = less than 
        )
        self.assertEqual(encontrado.exists(), False)

    def test_horas_prometidas(self):
        for cuanto in [10,20,30]:
            banco_registrar(
                quien_da=userA, 
                quien_recibe=userM, 
                titulo="no guardar cuanto negativo!", 
                cuanto=cuanto, 
                que="enseñar banda django"
            )
        banco_registrar(
                quien_da=userM, 
                quien_recibe=userA, 
                titulo="no guardar cuanto negativo!", 
                cuanto=3, 
                que="enseñar banda django"
            )  

        horas1 = horas_prometidas(userA) 
        print(f'las horas que debe son {horas1}')

        horas2 = horas_prometidas(userM)
        print(f'las horas que debe son {horas2}')

        self.assertEqual(horas1,60)
        self.assertEqual(horas2,3)

    def test_M_transfiere_a_X_horas_de_A(self):
        horas_de_A="horas de A para programar"
        for cuanto in [10,20,30]:
            banco_registrar(
                quien_da=userA, 
                quien_recibe=userM, 
                titulo="transferir a M", 
                cuanto=cuanto, 
                que=horas_de_A
            )
        #A: A le transfirio 10+20+30 hs a M

        banco_registrar(
            quien_da=userM, 
            quien_recibe=userX, 
            titulo="transferir a X", 
            cuanto=35, 
            que=horas_de_A, #A: el que es igual al que recibi.
            son_propias=False
        )
        #A: M las transferiere a X

        horas1 = horas_recibidas(userM,horas_de_A) 
        print(f'las horas que tiene A son {horas1}')

        horas2 = horas_recibidas(userX, horas_de_A)
        print(f'las horas que tiene M son {horas2}')

        #TODO: testear tambien con distinto que

        self.assertEqual(horas2, 35)
        
        banco_registrar(
            quien_da=userM, 
            quien_recibe=userX, 
            titulo="transferir a X", 
            cuanto=25, 
            que=horas_de_A, #A: el que es igual al que recibi.
            son_propias=False
        )
        #A: M las transferiere a X

        horas1 = horas_recibidas(userM,horas_de_A) 
        print(f'las horas que tiene A son {horas1}')

        horas2 = horas_recibidas(userX, horas_de_A)
        print(f'las horas que tiene M son {horas2}')

        #TODO: revisar que lanzo excepcion y que el saldo quedo bien.
        self.assertEqual(horas2, 60)