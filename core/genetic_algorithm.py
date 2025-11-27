# genetic_algorithm.py - REFORMULADO COM ANTI-ESTAGNAÇÃO
import random
import numpy as np
from typing import List, Tuple, Dict
from config import Config
from simulation import calcular_fitness

# ===========================
# POPULAÇÃO INICIAL DIVERSIFICADA
# ===========================
def populacao_inicial_balanceada(pop_size: int, n: int, idx_base: int) -> List[Dict]:
    """
    PROBLEMA: 80% com mesmas velocidades → convergência prematura
    SOLUÇÃO: Distribuição equilibrada (30%/30%/30%/10%)
    """
    pop = []
    
    # 30% velocidades BAIXAS (eficiente em bateria)
    num_baixa = int(pop_size * Config.INIT_VELOCIDADE_BAIXA)
    for _ in range(num_baixa):
        c = criar_cromossomo(n, idx_base)
        c['velocidades'] = [random.choice([36, 40, 44, 48, 52]) 
                           for _ in range(len(c['velocidades']))]
        pop.append(c)
    
    # 30% velocidades MÉDIAS (balanceado)
    num_media = int(pop_size * Config.INIT_VELOCIDADE_MEDIA)
    for _ in range(num_media):
        c = criar_cromossomo(n, idx_base)
        c['velocidades'] = [random.choice([56, 60, 64, 68, 72, 76]) 
                           for _ in range(len(c['velocidades']))]
        pop.append(c)
    
    # 30% velocidades ALTAS (rápido)
    num_alta = int(pop_size * Config.INIT_VELOCIDADE_ALTA)
    for _ in range(num_alta):
        c = criar_cromossomo(n, idx_base)
        c['velocidades'] = [random.choice([80, 84, 88, 92, 96]) 
                           for _ in range(len(c['velocidades']))]
        pop.append(c)
    
    # 10% COMPLETAMENTE ALEATÓRIO (diversidade máxima)
    while len(pop) < pop_size:
        pop.append(criar_cromossomo(n, idx_base))
    
    return pop


def criar_cromossomo(n: int, idx_base: int) -> Dict:
    """Cria cromossomo garantindo rota completa"""
    intermediarios = [i for i in range(n) if i != idx_base]
    random.shuffle(intermediarios)
    
    rota = [idx_base] + intermediarios + [idx_base]
    n_trechos = len(rota) - 1
    
    velocidades = [random.choice(Config.VELOCIDADES_VALIDAS) 
                   for _ in range(n_trechos)]
    
    return {"rota": rota, "velocidades": velocidades}


# ===========================
# OPERADORES GENÉTICOS
# ===========================
def selecao_torneio(pop: List[Dict], fitness: List[float], k: int) -> Dict:
    """Seleção por torneio"""
    indices = random.sample(range(len(pop)), k)
    vencedor = min(indices, key=lambda i: fitness[i] if fitness[i] != float('inf') else float('inf'))
    return {"rota": pop[vencedor]["rota"][:], 
            "velocidades": pop[vencedor]["velocidades"][:]}


def crossover_ox(p1: Dict, p2: Dict, idx_base: int) -> Tuple[Dict, Dict]:
    """Order Crossover preservando ordem"""
    r1 = p1["rota"][1:-1]
    r2 = p2["rota"][1:-1]
    n = len(r1)
    
    if n <= 1:
        return {"rota": p1["rota"][:], "velocidades": p1["velocidades"][:]}, \
               {"rota": p2["rota"][:], "velocidades": p2["velocidades"][:]}
    
    a, b = sorted(random.sample(range(n), 2))
    
    def ox_route(ra, rb):
        filho = [None] * n
        filho[a:b+1] = ra[a:b+1]
        
        idx_filho = (b + 1) % n
        idx_rb = (b + 1) % n
        
        while None in filho:
            if rb[idx_rb] not in filho:
                filho[idx_filho] = rb[idx_rb]
                idx_filho = (idx_filho + 1) % n
            idx_rb = (idx_rb + 1) % n
        
        return [idx_base] + filho + [idx_base]
    
    c1_rota = ox_route(r1, r2)
    c2_rota = ox_route(r2, r1)
    
    # Crossover de velocidades
    c1_vel = []
    c2_vel = []
    for v1, v2 in zip(p1["velocidades"], p2["velocidades"]):
        if random.random() < 0.5:
            c1_vel.append(v1)
            c2_vel.append(v2)
        else:
            c1_vel.append(v2)
            c2_vel.append(v1)
    
    return {"rota": c1_rota, "velocidades": c1_vel}, \
           {"rota": c2_rota, "velocidades": c2_vel}


def mutacao_multipla(cromossomo: Dict, taxa_base: float) -> None:
    """
    MUTAÇÃO MÚLTIPLA: Swap + Inversion + 2-opt
    Conforme documento: "swap + inversion (2-opt style)"
    """
    
    # 1. SWAP (trocar 2 posições)
    if random.random() < taxa_base:
        rota = cromossomo["rota"]
        if len(rota) > 3:
            i, j = random.sample(range(1, len(rota)-1), 2)
            rota[i], rota[j] = rota[j], rota[i]
    
    # 2. INVERSION (inverter segmento)
    if random.random() < Config.MUTATION_RATE_INVERSION:
        rota = cromossomo["rota"]
        if len(rota) > 3:
            i, j = sorted(random.sample(range(1, len(rota)-1), 2))
            rota[i:j+1] = list(reversed(rota[i:j+1]))
    
    # 3. 2-OPT (melhoria local)
    if random.random() < Config.MUTATION_RATE_2OPT:
        rota = cromossomo["rota"]
        if len(rota) > 4:
            i = random.randint(1, len(rota)-3)
            j = random.randint(i+2, len(rota)-1)
            rota[i:j] = reversed(rota[i:j])
    
    # 4. MUTAÇÃO DE VELOCIDADES
    velocidades = cromossomo["velocidades"]
    for i in range(len(velocidades)):
        if random.random() < taxa_base:
            # 70%: mudança gradual (±4 ou ±8 km/h)
            if random.random() < 0.7:
                delta = random.choice([-8, -4, 4, 8])
                nova_vel = velocidades[i] + delta
                nova_vel = max(36, min(96, nova_vel))
                nova_vel = (nova_vel // 4) * 4
                velocidades[i] = nova_vel
            else:
                # 30%: mudança radical
                velocidades[i] = random.choice(Config.VELOCIDADES_VALIDAS)


def local_search_2opt(cromossomo: Dict, dist_matrix: List[List[float]]) -> Dict:
    """
    2-OPT LOCAL SEARCH
    Conforme documento: "2-opt local search aplicado aos 5-10 melhores filhos"
    """
    rota = cromossomo["rota"][:]
    melhorou = True
    
    while melhorou:
        melhorou = False
        
        for i in range(1, len(rota) - 2):
            for j in range(i + 2, len(rota) - 1):
                # Calcula distância atual
                dist_antes = (dist_matrix[rota[i-1]][rota[i]] +
                             dist_matrix[rota[j]][rota[j+1]])
                
                # Calcula distância se inverter
                dist_depois = (dist_matrix[rota[i-1]][rota[j]] +
                              dist_matrix[rota[i]][rota[j+1]])
                
                # Se melhorou, aplica
                if dist_depois < dist_antes:
                    rota[i:j+1] = reversed(rota[i:j+1])
                    melhorou = True
                    break
            
            if melhorou:
                break
    
    return {"rota": rota, "velocidades": cromossomo["velocidades"][:]}


# ===========================
# MONITORAMENTO E DIAGNÓSTICO
# ===========================
def calcular_estatisticas(fitness: List[float]) -> Dict:
    """Calcula estatísticas da geração"""
    fitness_validos = [f for f in fitness if f != float('inf')]
    
    if not fitness_validos:
        return {
            'minimo': float('inf'),
            'maximo': float('inf'),
            'media': float('inf'),
            'mediana': float('inf'),
            'desvio': 0.0,
            'num_validos': 0
        }
    
    return {
        'minimo': min(fitness_validos),
        'maximo': max(fitness_validos),
        'media': np.mean(fitness_validos),
        'mediana': np.median(fitness_validos),
        'desvio': np.std(fitness_validos),
        'num_validos': len(fitness_validos)
    }


def detectar_estagnacao(historico_media: List[float], geracoes_check: int = 20) -> Tuple[bool, float]:
    """
    DETECÇÃO DE ESTAGNAÇÃO
    Conforme documento: "calcule a inclinação (slope) da série mean_fitness 
    nas últimas 20 gens por regressão linear simples"
    """
    if len(historico_media) < geracoes_check + 1:
        return False, 0.0
    
    # Pega últimas N gerações
    ultimas = historico_media[-geracoes_check:]
    
    # Regressão linear simples
    x = np.arange(len(ultimas))
    y = np.array(ultimas)
    
    # Calcula slope
    slope = np.polyfit(x, y, 1)[0]
    
    # Calcula melhoria percentual
    if ultimas[0] > 0:
        melhoria_pct = ((ultimas[0] - ultimas[-1]) / ultimas[0]) * 100
    else:
        melhoria_pct = 0.0
    
    # Estagnado se melhoria < threshold
    estagnado = melhoria_pct < Config.STAGNATION_THRESHOLD
    
    return estagnado, melhoria_pct


# ===========================
# ESTRATÉGIAS ANTI-ESTAGNAÇÃO
# ===========================
def restart_parcial(pop: List[Dict], fitness: List[float], n: int, idx_base: int) -> List[Dict]:
    """
    RESTART PARCIAL
    Conforme documento: "reinicializar 20-40% da população"
    """
    # Ordena por fitness
    sorted_idx = sorted(range(len(pop)), key=lambda i: fitness[i])
    
    # Mantém os melhores
    num_manter = int(len(pop) * (1 - Config.RESTART_PERCENTAGE))
    nova_pop = [{"rota": pop[i]["rota"][:], "velocidades": pop[i]["velocidades"][:]} 
                for i in sorted_idx[:num_manter]]
    
    # Gera novos aleatórios
    while len(nova_pop) < len(pop):
        nova_pop.append(criar_cromossomo(n, idx_base))
    
    return nova_pop


def hypermutation(cromossomo: Dict) -> None:
    """
    HIPER-MUTAÇÃO
    Conforme documento: "mutação pesada após estagnação"
    """
    # Múltiplas mutações fortes
    for _ in range(3):
        mutacao_multipla(cromossomo, Config.HYPERMUTATION_RATE)


# ===========================
# ALGORITMO GENÉTICO PRINCIPAL
# ===========================
def evolve_optimized(ceps: List[str], coords: List[Tuple[float,float]],
                    dist_matrix: List[List[float]], idx_base: int,
                    wind_cache: Dict, pop_size: int, generations: int, verbose: bool = True):
    """
    AG REFORMULADO COM ANTI-ESTAGNAÇÃO
    
    Melhorias implementadas:
    1. Escala lexicográfica correta (fitness detecta melhorias)
    2. População inicial balanceada (30%/30%/30%/10%)
    3. Múltiplos operadores de mutação (swap + inversion + 2-opt)
    4. Detecção de estagnação (regressão linear em 20 gerações)
    5. Estratégias de recuperação (restart + hypermutation + local search)
    6. Monitoramento completo (min/média/mediana/desvio)
    """
    n = len(ceps)
    
    # População inicial BALANCEADA
    print(f"\nGerando população inicial balanceada...")
    pop = populacao_inicial_balanceada(pop_size, n, idx_base)
    fitness = [calcular_fitness(ind, coords, dist_matrix, wind_cache) for ind in pop]
    
    # Estatísticas iniciais
    stats = calcular_estatisticas(fitness)
    
    melhor_idx = min(range(len(pop)), 
                     key=lambda i: fitness[i] if fitness[i] != float('inf') else float('inf'))
    melhor = {"rota": pop[melhor_idx]["rota"][:], 
              "velocidades": pop[melhor_idx]["velocidades"][:]}
    melhor_fit = fitness[melhor_idx]
    
    # Histórico
    historico = {
        'minimo': [stats['minimo']],
        'media': [stats['media']],
        'mediana': [stats['mediana']],
        'maximo': [stats['maximo']],
        'desvio': [stats['desvio']],
        'num_validos': [stats['num_validos']]
    }
    
    if verbose:
        print(f"\n{'='*100}")
        print(f"{'GERAÇÃO 0 (INICIAL)':^100}")
        print(f"{'='*100}")
        print(f"  Mínimo:  {stats['minimo']:>15,.0f}")
        print(f"  Média:   {stats['media']:>15,.0f}")
        print(f"  Mediana: {stats['mediana']:>15,.0f}")
        print(f"  Máximo:  {stats['maximo']:>15,.0f}")
        print(f"  Desvio:  {stats['desvio']:>15,.0f}")
        print(f"  Viáveis: {stats['num_validos']:>3} / {len(pop):>3}")
        print(f"{'='*100}\n")
    
    # Validação da escala
    if verbose and Config.validar_escala:
        Config.validar_escala()
    
    geracoes_sem_melhoria = 0
    
    # Evolução
    for gen in range(generations):
        nova_pop = []
        sorted_idx = sorted(range(len(pop)), key=lambda i: fitness[i])
        
        # ELITISMO
        for i in range(Config.ELITISM_COUNT):
            nova_pop.append({
                "rota": pop[sorted_idx[i]]["rota"][:],
                "velocidades": pop[sorted_idx[i]]["velocidades"][:]
            })
        
        # CROSSOVER + MUTAÇÃO
        while len(nova_pop) < pop_size:
            p1 = selecao_torneio(pop, fitness, Config.TOURNAMENT_SIZE)
            p2 = selecao_torneio(pop, fitness, Config.TOURNAMENT_SIZE)
            
            if random.random() < Config.CROSSOVER_RATE:
                c1, c2 = crossover_ox(p1, p2, idx_base)
            else:
                c1 = {"rota": p1["rota"][:], "velocidades": p1["velocidades"][:]}
                c2 = {"rota": p2["rota"][:], "velocidades": p2["velocidades"][:]}
            
            mutacao_multipla(c1, Config.MUTATION_RATE_SWAP)
            mutacao_multipla(c2, Config.MUTATION_RATE_SWAP)
            
            nova_pop.extend([c1, c2])
        
        # LOCAL SEARCH nos melhores
        if (gen + 1) % 10 == 0:
            for i in range(Config.LOCAL_SEARCH_ELITE):
                if i < len(nova_pop):
                    nova_pop[i] = local_search_2opt(nova_pop[i], dist_matrix)
        
        pop = nova_pop[:pop_size]
        fitness = [calcular_fitness(ind, coords, dist_matrix, wind_cache) for ind in pop]
        
        # Estatísticas
        stats = calcular_estatisticas(fitness)
        
        historico['minimo'].append(stats['minimo'])
        historico['media'].append(stats['media'])
        historico['mediana'].append(stats['mediana'])
        historico['maximo'].append(stats['maximo'])
        historico['desvio'].append(stats['desvio'])
        historico['num_validos'].append(stats['num_validos'])
        
        # Atualiza melhor
        if stats['minimo'] < melhor_fit and stats['minimo'] != float('inf'):
            melhoria = ((melhor_fit - stats['minimo']) / melhor_fit) * 100
            melhor_fit = stats['minimo']
            melhor_idx = min(range(len(pop)), 
                            key=lambda i: fitness[i] if fitness[i] != float('inf') else float('inf'))
            melhor = {"rota": pop[melhor_idx]["rota"][:],
                     "velocidades": pop[melhor_idx]["velocidades"][:]}
            geracoes_sem_melhoria = 0
            
            if verbose:
                print(f"Gen {gen+1:3d} | ✓ MELHORIA: {melhor_fit:,.0f} (-{melhoria:.2f}%)")
        else:
            geracoes_sem_melhoria += 1
        
        # Monitoramento
        if verbose and (gen + 1) % Config.PRINT_EVERY == 0:
            print(f"Gen {gen+1:3d} | "
                  f"Min: {stats['minimo']:10,.0f} | "
                  f"Média: {stats['media']:10,.0f} | "
                  f"Desvio: {stats['desvio']:8,.0f} | "
                  f"Viáveis: {stats['num_validos']}/{len(pop)}")
        
        # DETECÇÃO DE ESTAGNAÇÃO (a cada 20 gerações)
        if (gen + 1) % Config.STAGNATION_CHECK == 0:
            estagnado, melhoria_pct = detectar_estagnacao(historico['media'])
            
            if verbose:
                print(f"\n{'─'*100}")
                print(f"DIAGNÓSTICO (Últimas {Config.STAGNATION_CHECK} Gerações):")
                print(f"  Melhoria: {melhoria_pct:.2f}%")
                
                if estagnado:
                    print(f"  Status: ⚠ ESTAGNADO (< {Config.STAGNATION_THRESHOLD}%)")
                    print(f"  Ação: Aplicando estratégias de recuperação...")
                else:
                    print(f"  Status: ✓ CONVERGINDO ({melhoria_pct:.2f}%)")
                print(f"{'─'*100}\n")
            
            # ESTRATÉGIAS ANTI-ESTAGNAÇÃO
            if estagnado:
                # 1. Restart parcial
                pop = restart_parcial(pop, fitness, n, idx_base)
                
                # 2. Hiper-mutação nos piores
                for i in range(len(pop) // 2, len(pop)):
                    hypermutation(pop[i])
                
                # Recalcula fitness
                fitness = [calcular_fitness(ind, coords, dist_matrix, wind_cache) for ind in pop]
                
                if verbose:
                    print(f"  → Restart parcial aplicado ({Config.RESTART_PERCENTAGE*100:.0f}% novos)")
                    print(f"  → Hiper-mutação aplicada em 50% da população")
    
    return melhor, melhor_fit, historico