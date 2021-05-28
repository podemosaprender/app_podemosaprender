#INFO: testear el correcto funcionamiento del banquito de horas.

from .util import BaseTextCase
from pa_charlas_app.models_banco import *
from pa_charlas_app.models import User

# Caso1: A anota que le debe 4 horas a M (M lo puede ver, no se puede cambiar. Esas horas solo las puede transferir o gastar M)
# Caso2: Sabemos cuantas horas A tiene prometidas a otras personas.
# Caso3: M le transfiere dos horas de A a X.
#   1. que M las tenga. 
#   2. que no quede en negativo
# Caso4: X confirma que A ya no le debe las horas.

class BancoTxTest(BaseTextCase):
    def test_crear_transaccion(self):
        userA = User.objects.get(pk=3)
        userM = User.objects.get(pk=1)
        userX = User.objects.get(pk=2)
        
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
        userA = User.objects.get(pk=3)
        userM = User.objects.get(pk=1)
        userX = User.objects.get(pk=2)

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

    def test_hs_prometidas(self):
        userA = User.objects.get(pk=3)
        userM = User.objects.get(pk=1)
        userX = User.objects.get(pk=2)

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

        horas1 = hs_prometidas(userA) 
        print(f'las horas que debe son {horas1}')

        horas2 = hs_prometidas(userM)
        print(f'las horas que debe son {horas2}')

        self.assertEqual(horas1,60)
        self.assertEqual(horas2,3)

    def test_M_transfiere_a_X_horas_de_A(self):
        userA = User.objects.get(pk=3)
        userM = User.objects.get(pk=1)
        userX = User.objects.get(pk=2)

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

        a_M_le_quedan_hs = hs_para_usar(userM,horas_de_A) 
        print(f'las horas que tiene A son {a_M_le_quedan_hs}')

        a_X_le_quedan_hs = hs_para_usar(userX, horas_de_A)
        print(f'las horas que tiene M son {a_X_le_quedan_hs}')

        #TODO: testear tambien con distinto que

        self.assertEqual(a_M_le_quedan_hs, 60)
        self.assertEqual(a_X_le_quedan_hs, 0)
        
        banco_registrar(
            quien_da=userM, 
            quien_recibe=userX, 
            quien_hace= userA,
            titulo="transferir a X", 
            cuanto=35, 
            que=horas_de_A, #A: el que es igual al que recibi.
        )
        #A: M las transferiere a X

        a_M_le_quedan_hs = hs_para_usar(userM,horas_de_A) 
        print(f'las horas que tiene A son {a_M_le_quedan_hs}')

        a_X_le_quedan_hs = hs_para_usar(userX, horas_de_A)
        print(f'las horas que tiene M son {a_X_le_quedan_hs}')

        #TODO: testear tambien con distinto que

        self.assertEqual(a_M_le_quedan_hs, 60-35)
        self.assertEqual(a_X_le_quedan_hs, 35)
        
        with self.assertRaises(ValueError):
            banco_registrar(
                quien_da=userM, 
                quien_recibe=userX, 
                titulo="transferir a X", 
                cuanto=26, #A: son mas horas de las que tiene
                que=horas_de_A, #A: el que es igual al que recibi.
                quien_hace = userA
            )
        #A: M las transferiere a X

        self.assertEqual(a_M_le_quedan_hs, 60-35)
        self.assertEqual(a_X_le_quedan_hs, 35)
        #A: no cambio porque lanzo excepcion

        banco_registrar(
            quien_da=userM, 
            quien_recibe=userX, 
            titulo="transferir a X", 
            cuanto=25, 
            que=horas_de_A, #A: el que es igual al que recibi.
            quien_hace = userA
        )
        #A: M las transferiere a X

        a_M_le_quedan_hs = hs_para_usar(userM,horas_de_A) 
        print(f'las horas que tiene A son {a_M_le_quedan_hs}')

        a_X_le_quedan_hs = hs_para_usar(userX, horas_de_A)
        print(f'las horas que tiene M son {a_X_le_quedan_hs}')

        self.assertEqual(a_M_le_quedan_hs, 0)
        self.assertEqual(a_X_le_quedan_hs, 60)
