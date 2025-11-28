import unittest
import math
from typing import List, Tuple, Dict

# Importa as funções e classes a serem testadas
from physics import DronePhysics, bearing

# ====================================================================
# TESTE 2: physics.py - simular_trecho_com_fisica e calcular_velocidade_com_vento
# ====================================================================
class TestDronePhysics(unittest.TestCase):
    
    def test_bearing(self):
        """Testa o cálculo da direção (bearing) entre dois pontos."""
        # 1. Norte (0 graus)
        lat1, lon1 = 0.0, 0.0
        lat2, lon2 = 1.0, 0.0
        self.assertAlmostEqual(bearing(lat1, lon1, lat2, lon2), 0.0, delta=0.01)
        
        # 2. Leste (90 graus)
        lat1, lon1 = 0.0, 0.0
        lat2, lon2 = 0.0, 1.0
        self.assertAlmostEqual(bearing(lat1, lon1, lat2, lon2), 90.0, delta=0.01)
        
        # 3. Sul (180 graus)
        lat1, lon1 = 1.0, 0.0
        lat2, lon2 = 0.0, 0.0
        self.assertAlmostEqual(bearing(lat1, lon1, lat2, lon2), 180.0, delta=0.01)
        
        # 4. Oeste (270 graus)
        lat1, lon1 = 0.0, 1.0
        lat2, lon2 = 0.0, 0.0
        self.assertAlmostEqual(bearing(lat1, lon1, lat2, lon2), 270.0, delta=0.01)

    def test_calcular_velocidade_com_vento(self):
        """Testa o cálculo da velocidade efetiva com vento."""
        v_drone_ms = 20.0  # 72 km/h
        vento_kmh = 36.0   # 10 m/s
        
        # 1. Vento a favor (0 graus relativo)
        v_efetiva_favor = DronePhysics.calcular_velocidade_com_vento(
            v_drone_ms, dir_drone_graus=90, vento_kmh=vento_kmh, dir_vento_graus=90
        )
        # Esperado: 20 m/s + 10 m/s = 30 m/s
        self.assertAlmostEqual(v_efetiva_favor, 30.0, delta=0.01)
        
        # 2. Vento contrário (180 graus relativo)
        v_efetiva_contra = DronePhysics.calcular_velocidade_com_vento(
            v_drone_ms, dir_drone_graus=90, vento_kmh=vento_kmh, dir_vento_graus=270
        )
        # Esperado: 20 m/s - 10 m/s = 10 m/s
        self.assertAlmostEqual(v_efetiva_contra, 10.0, delta=0.01)
        
        # 3. Vento lateral (90 graus relativo)
        v_efetiva_lateral = DronePhysics.calcular_velocidade_com_vento(
            v_drone_ms, dir_drone_graus=90, vento_kmh=vento_kmh, dir_vento_graus=0
        )
        # Esperado: 20 m/s + 10 m/s * cos(90) = 20 m/s
        self.assertAlmostEqual(v_efetiva_lateral, 20.0, delta=0.01)

    def test_simular_trecho_sem_vento(self):
        """Testa a simulação de um trecho simples sem vento."""
        dist_km = 1.0
        v_inicial = 0.0
        v_cruzeiro = 72.0  # 20 m/s
        
        tempo, consumo, v_final = DronePhysics.simular_trecho_com_fisica(
            dist_km, v_inicial, v_cruzeiro
        )
        
        # Tempo total esperado: 58.34 segundos (calculado na análise anterior)
        self.assertAlmostEqual(tempo, 58.34, delta=0.1)
        self.assertAlmostEqual(v_final, 0.0, delta=0.01)
        # Consumo total esperado: 183.35 segundos (calculado na análise anterior)
        self.assertAlmostEqual(consumo, 183.35, delta=0.5)

if __name__ == '__main__':
    unittest.main()
