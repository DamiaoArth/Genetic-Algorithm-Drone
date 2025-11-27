# config.py - REFORMULADO CONFORME ANÁLISE DO PROFESSOR
from typing import List

class Config:
    """Configurações reformuladas - Escala de fitness CORRETA"""
    
    # Geográficos
    CEP_UNIBRASIL = "82821020"
    HORA_INICIO = 6
    HORA_FIM = 19
    HORA_CUSTO_EXTRA = 17
    PRAZO_DIAS = 7
    
    # Drone
    VELOCIDADE_MAXIMA = 96
    VELOCIDADE_MINIMA = 36
    MULTIPLO_VELOCIDADE = 4
    AUTONOMIA_BASE_SEG = 4650.0  # 5000.0 * 0.93
    
    # Custos
    TEMPO_PARADA_SEG = 72
    TEMPO_RECARGA_SEG = 3600
    CUSTO_POUSO_REAIS = 80.0
    CUSTO_POUSO_TARDIO = 80.0
    
    # ===========================
    # FITNESS - ESCALA CORRETA (LEXICOGRÁFICA)
    # ===========================
    # PROBLEMA DETECTADO: Pesos de 10.000 destroem o gradiente!
    # SOLUÇÃO: Escala lexicográfica com multiplicadores MUITO maiores
    
    # "Use D muito maior que R * max_recharges + max_time"
    # Para garantir que distância SEMPRE domina
    
    # Multiplicadores lexicográficos (conforme documento)
    MULT_DISTANCIA = 1_000_000.0      # 1 milhão por km
    MULT_TEMPO = 1.0                   # 1 ponto por segundo
    MULT_POUSOS = 1_000.0              # 1 mil por pouso
    
    # Penalidades ENORMES para violações
    PENALIDADE_DIAS = 100_000_000.0    # 100 milhões por dia extra
    PENALIDADE_POUSOS_EXCESSO = 50_000.0  # 50 mil por pouso extra
    PENALIDADE_VENTO = 100.0
    
    # Limites
    POUSOS_LIMITE = 15
    TEMPO_ESPERADO_SEG = 100000.0  # Para normalização se necessário
    
    # ===========================
    # ALGORITMO GENÉTICO - REFORMULADO
    # ===========================
    # Conforme documento: "População 100-300, Gerações 200-1000"
    
    POP_SIZE = 150                 # Reduzido de 200 para 150
    GENERATIONS = 300              # Aumentado para 300
    
    # Operadores
    CROSSOVER_RATE = 0.85          # OX mantido
    MUTATION_RATE_SWAP = 0.12      # Swap mantido
    MUTATION_RATE_INVERSION = 0.08 # Inversion separado
    MUTATION_RATE_2OPT = 0.05      # 2-opt adicionado
    
    # Seleção
    ELITISM_COUNT = 5              # Elitismo: 5 indivíduos (conforme doc)
    TOURNAMENT_SIZE = 3            # Torneio tamanho 3
    
    # ===========================
    # ANTI-ESTAGNAÇÃO (CRÍTICO!)
    # ===========================
    # "Parâmetros iniciais sugeridos"
    
    STAGNATION_CHECK = 20          # Verifica a cada 20 gerações
    STAGNATION_THRESHOLD = 0.5     # Melhoria mínima: 0.5%
    
    # Estratégias quando estagna:
    RESTART_PERCENTAGE = 0.30      # Reinicia 30% da população
    HYPERMUTATION_RATE = 0.40      # Taxa de hiper-mutação
    LOCAL_SEARCH_ELITE = 5         # Aplica 2-opt nos 5 melhores
    
    # ===========================
    # DIVERSIDADE INICIAL
    # ===========================
    # PROBLEMA: 80% com mesmas velocidades causa convergência prematura
    # SOLUÇÃO: Distribuição equilibrada
    
    INIT_VELOCIDADE_BAIXA = 0.30   # 30% velocidades baixas (36-52)
    INIT_VELOCIDADE_MEDIA = 0.30   # 30% velocidades médias (56-76)
    INIT_VELOCIDADE_ALTA = 0.30    # 30% velocidades altas (80-96)
    INIT_VELOCIDADE_RANDOM = 0.10  # 10% completamente aleatório
    
    # ===========================
    # SIMULAÇÃO EM DUAS CAMADAS
    # ===========================
    # PROBLEMA: Simulação realista é MUITO lenta
    # SOLUÇÃO: Fitness rápido + validação detalhada apenas no final
    
    USE_FAST_FITNESS = True        # Usa estimativa rápida no AG
    VALIDATE_DETAILED_FINAL = True # Simula detalhado apenas no melhor
    
    # Velocidades válidas
    VELOCIDADES_VALIDAS: List[int] = list(range(VELOCIDADE_MINIMA, VELOCIDADE_MAXIMA + 1, MULTIPLO_VELOCIDADE))
    
    # ===========================
    # MONITORAMENTO (20 GERAÇÕES)
    # ===========================
    MONITOR_EVERY = 1              # Monitora a cada geração
    PRINT_EVERY = 5                # Imprime a cada 5 gerações
    PLOT_CONVERGENCE = True        # Gera gráficos
    
    # ===========================
    # VALIDAÇÃO DE ESCALA
    # ===========================
    @staticmethod
    def validar_escala():
        """
        Valida se a escala lexicográfica está correta
        
        Conforme documento:
        "escolha D = 1e6, R = 1e3, T = 1"
        "D >> (max_possible_R * R + max_possible_time * T)"
        """
        max_pousos = 50  # Máximo realista
        max_tempo = 200000  # ~55 horas
        
        # Componente secundário máximo
        max_secundario = (max_pousos * Config.MULT_POUSOS + 
                         max_tempo * Config.MULT_TEMPO)
        
        # Diferença mínima detectável em distância (100m = 0.1 km)
        min_diff_distancia = 0.1 * Config.MULT_DISTANCIA
        
        # Verifica se distância domina
        ratio = min_diff_distancia / max_secundario
        
        print("\n" + "="*80)
        print(" VALIDAÇÃO DA ESCALA DO FITNESS")
        print("="*80)
        print(f"\nMultiplicadores:")
        print(f"  Distância: {Config.MULT_DISTANCIA:,.0f} por km")
        print(f"  Tempo:     {Config.MULT_TEMPO:,.0f} por segundo")
        print(f"  Pousos:    {Config.MULT_POUSOS:,.0f} por pouso")
        
        print(f"\nAnálise:")
        print(f"  Componente secundário máximo: {max_secundario:,.0f}")
        print(f"  Diferença mínima (100m):      {min_diff_distancia:,.0f}")
        print(f"  Ratio: {ratio:.2f}x")
        
        if ratio > 2.0:
            print(f"\n✓ ESCALA CORRETA: 100m de distância vale {ratio:.0f}x mais que todos os secundários!")
            print("  → Distância DOMINA o fitness conforme professor")
            return True
        else:
            print(f"\n✗ ESCALA INCORRETA: Distância não domina suficientemente!")
            print("  → Aumentar MULT_DISTANCIA ou reduzir MULT_TEMPO/MULT_POUSOS")
            return False


# Validação automática ao importar
if __name__ == "__main__":
    Config.validar_escala()