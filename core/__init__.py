"""
UNIBRASIL Surveyor - Core Module

Módulo principal contendo toda a lógica do sistema de
otimização de rotas para drone autônomo usando Algoritmo Genético.

Componentes:
    - config: Configurações e parâmetros do sistema
    - data_loader: Carregamento e processamento de dados
    - physics: Física do drone (aceleração, vento, consumo)
    - simulation: Simulação de rotas e cálculo de fitness
    - genetic_algorithm: Implementação do AG
    - visualizacao: Geração de gráficos e visualizações

Autores: [PREENCHER COM NOMES E MATRÍCULAS]
Disciplina: Serviços Cognitivos
Professor: Mozart Hasse
Instituição: Unibrasil
Data: 2025
"""

__version__ = "1.0.0"
__author__ = "Equipe UNIBRASIL"

# Imports principais para facilitar uso do módulo
from .config import Config
from .data_loader import (
    load_ceps_coords,
    generate_distance_matrix,
    build_wind_cache,
    validar_arquivo_csv
)
from .simulation import (
    calcular_fitness,
    simulate_route_detailed,
    validate_solution
)
from .genetic_algorithm import (
    evolve_optimized,
    criar_cromossomo,
    populacao_inicial_balanceada
)

__all__ = [
    # Config
    'Config',
    
    # Data Loader
    'load_ceps_coords',
    'generate_distance_matrix',
    'build_wind_cache',
    'validar_arquivo_csv',
    
    # Simulation
    'calcular_fitness',
    'simulate_route_detailed',
    'validate_solution',
    
    # Genetic Algorithm
    'evolve_optimized',
    'criar_cromossomo',
    'populacao_inicial_balanceada',
]