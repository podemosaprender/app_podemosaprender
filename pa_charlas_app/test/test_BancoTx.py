#INFO: testear el correcto funcionamiento del banquito de horas.

from .util import BaseTextCase
from pa_charlas_app.models import *

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

        
