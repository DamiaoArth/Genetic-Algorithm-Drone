import unittest
import math
from typing import List, Tuple, Dict

# Importa as funções e classes a serem testadas
from simulation import calcular_fitness
from config import Config # Necessário para o fitness
from data_loader import generate_distance_matrix # Necessário para gerar dados de teste

# ====================================================================
# TESTE 3: simulation.py - calcular_fitness (Lexicográfico)
# ====================================================================
class TestSimulation(unittest.TestCase):
    
    def setUp(self):
        """Configuração de dados de teste para o fitness."""
        # Mock de Config (garante que os valores de teste são usados)
        self.original_mult_distancia = Config.MULT_DISTANCIA
        self.original_mult_pousos = Config.MULT_POUSOS
        self.original_mult_tempo = Config.MULT_TEMPO
        self.original_use_fast_fitness = Config.USE_FAST_FITNESS
        self.original_prazo_dias = Config.PRAZO_DIAS
        self.original_pousos_limite = Config.POUSOS_LIMITE
        
        Config.MULT_DISTANCIA = 1_000_000.0
        Config.MULT_POUSOS = 1_000.0
        Config.MULT_TEMPO = 1.0
        Config.USE_FAST_FITNESS = True # Usa a simulação rápida para o teste
        Config.PRAZO_DIAS = 7
        Config.POUSOS_LIMITE = 15
        
        # Dados de teste
        self.coords = [(-25.0, -49.0), (-25.1, -49.1), (-25.2, -49.2)]
        self.dist_matrix = generate_distance_matrix(self.coords)
        self.wind_cache = {(1, 6): (0.0, 0.0)} # Sem vento
        
        # Cromossomo de teste (Rota: 0 -> 1 -> 2 -> 0)
        self.cromossomo_base = {
            "rota": [0, 1, 2, 0],
            "velocidades": [72, 72, 72]
        }
        
        # Mock da simulação rápida para valores conhecidos
        # simular_rapido_simples(cromossomo, coords, dist_matrix, wind_cache)
        # Retorna: distancia_total, tempo_total_seg, pousos, dias_usados, penalidade_vento
        self.mock_simulacao = lambda c, co, dm, wc: (
            10.0, # 10 km
            3600.0, # 1 hora
            5, # 5 pousos
            1, # 1 dia
            0.0 # Sem penalidade de vento
        )
        
        # Substitui a função real pela mock para isolar o teste do cálculo do fitness
        import simulation
        self.original_simular_rapido_simples = simulation.simular_rapido_simples
        simulation.simular_rapido_simples = self.mock_simulacao

    def tearDown(self):
        """Restaura as configurações originais."""
        Config.MULT_DISTANCIA = self.original_mult_distancia
        Config.MULT_POUSOS = self.original_mult_pousos
        Config.MULT_TEMPO = self.original_mult_tempo
        Config.USE_FAST_FITNESS = self.original_use_fast_fitness
        Config.PRAZO_DIAS = self.original_prazo_dias
        Config.POUSOS_LIMITE = self.original_pousos_limite
        
        # Restaura a função original
        import simulation
        simulation.simular_rapido_simples = self.original_simular_rapido_simples

    def test_fitness_base(self):
        """Testa o cálculo do fitness com valores base (sem penalidades)."""
        
        # Valores mockados:
        # Distância: 10.0 km
        # Tempo: 3600.0 segundos
        # Pousos: 5
        # Dias: 1
        
        # Esperado:
        # Custo Distância: 10.0 * 1.000.000 = 10.000.000
        # Custo Pousos: 5 * 1.000 = 5.000
        # Custo Tempo: 3600.0 * 1.0 = 3.600
        # Total: 10.000.000 + 5.000 + 3.600 = 10.008.600
        
        fitness = calcular_fitness(self.cromossomo_base, self.coords, self.dist_matrix, self.wind_cache)
        
        self.assertAlmostEqual(fitness, 10008600.0, delta=0.01)

    def test_fitness_penalidade_dias(self):
        """Testa o cálculo do fitness com penalidade por excesso de dias."""
        
        # Mock com 8 dias (1 dia a mais que o limite de 7)
        dias_excedidos_mock = lambda c, co, dm, wc: (10.0, 3600.0, 5, 8, 0.0)
        
        import simulation
        simulation.simular_rapido_simples = dias_excedidos_mock
        
        # Penalidade Dias: 1 * 100.000.000 = 100.000.000
        # Base: 10.008.600
        # Total: 110.008.600
        
        fitness = calcular_fitness(self.cromossomo_base, self.coords, self.dist_matrix, self.wind_cache)
        
        self.assertAlmostEqual(fitness, 110008600.0, delta=0.01)

    def test_fitness_penalidade_pousos(self):
        """Testa o cálculo do fitness com penalidade por excesso de pousos."""
        
        # Mock com 16 pousos (1 a mais que o limite de 15)
        pousos_excedidos_mock = lambda c, co, dm, wc: (10.0, 3600.0, 16, 1, 0.0)
        
        import simulation
        simulation.simular_rapido_simples = pousos_excedidos_mock
        
        # Penalidade Pousos: 1 * 50.000 = 50.000
        # Base: 10.008.600
        # Custo Pousos: 16 * 1.000 = 16.000
        # Novo Base: 10.000.000 + 16.000 + 3.600 = 10.019.600
        # Total: 10.019.600 + 50.000 = 10.069.600
        
        # O erro anterior era que eu estava usando o custo base de 5 pousos (5000) em vez de 16 pousos (16000)
        # O valor correto é 10.069.600.
        
        fitness = calcular_fitness(self.cromossomo_base, self.coords, self.dist_matrix, self.wind_cache)
        
        self.assertAlmostEqual(fitness, 10069600.0, delta=0.01)

if __name__ == '__main__':
    unittest.main()
