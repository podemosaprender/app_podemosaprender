#INFO: testear el correcto funcionamiento del banquito de horas.

from .util import BaseTextCase
from pa_charlas_app.models import *
from django.db.models import Sum

# Caso1: A anota que le debe 4 horas a M (M lo puede ver, no se puede cambiar. Esas horas solo las puede transferir o gastar M)
# Caso2: Sabemos cuantas horas A tiene prometidas a otras personas.
# Caso3: M le transfiere dos horas de A a X. 
# Caso4: X confirma que A ya no le debe las horas.

# Ejemplo de que: "horas de consultoria de Mauri"

def banco_registrar(quien_da, quien_recibe, cuanto, que="horas", titulo=None):
    #TODO: cuanto no puede ser negativo!
    #TODO: quien_da solo debe el usuario activo.
    #TODO: podria tener fecha de expiracion
    #TODO: podria tener una condicion ejecutable (url tipo smart contract)

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

def horas_prometidas(user):
    #VER: https://docs.djangoproject.com/en/3.2/topics/db/aggregation/#cheat-sheet
    horas = BancoTx.objects.filter(quien_da=user).aggregate(Sum('cuanto'))
    return horas['cuanto__sum']

user1 = User.objects.get(pk=1)
user2 = User.objects.get(pk=2)

class BancoTxTest(BaseTextCase):
    def test_crear_transaccion(self):

        
        banco_registrar(
            quien_da=user1, 
            quien_recibe=user2, 
            titulo="transaccion de prueba", 
            cuanto=10, 
            que="enseñar banda django"
        )

        encontrado = BancoTx.objects.filter(
            quien_da=user1, 
            quien_recibe=user2, 
            titulo="transaccion de prueba", 
            cuanto=10, 
            que="enseñar banda django"
        )
        self.assertEqual(encontrado.exists(),True)

    def test_cuanto_no_negativo(self):
        with self.assertRaises(ValueError):
            banco_registrar(
                quien_da=user1, 
                quien_recibe=user2, 
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
                quien_da=user1, 
                quien_recibe=user2, 
                titulo="no guardar cuanto negativo!", 
                cuanto=cuanto, 
                que="enseñar banda django"
            )
        banco_registrar(
                quien_da=user2, 
                quien_recibe=user1, 
                titulo="no guardar cuanto negativo!", 
                cuanto=3, 
                que="enseñar banda django"
            )  

        horas1 = horas_prometidas(user1) 
        print(f'las horas que debe son {horas1}')

        horas2 = horas_prometidas(user2)
        print(f'las horas que debe son {horas2}')

        self.assertEqual(horas1,60)
        self.assertEqual(horas2,3)
