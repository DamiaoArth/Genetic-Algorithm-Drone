# simulation.py - COMPLETO E REFORMULADO
import math
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from config import Config

from physics import DronePhysics, bearing

def calcular_dia_semana(dt: datetime) -> int:
    """Calcula dia da semana (1-7)"""
    base = datetime(2025, 1, 1)
    dias_passados = (dt.toordinal() - base.toordinal())
    return (dias_passados % 7) + 1

def get_wind_slot(dt: datetime, wind_cache: Dict) -> Tuple[float, float]:
    """Obtém vento para datetime específico"""
    dia = calcular_dia_semana(dt)
    hora = dt.hour
    
    slots = [18, 15, 12, 9, 6]
    slot = next((s for s in slots if hora >= s), 6)
    
    return wind_cache.get((dia, slot), (0.0, 0.0))

# ===========================
# FITNESS LEXICOGRÁFICO - ESCALA CORRETA
# ===========================
def calcular_fitness(cromossomo: Dict, coords: List[Tuple[float,float]],
                    dist_matrix: List[List[float]], wind_cache: Dict) -> float:
    """
    FITNESS LEXICOGRÁFICO COM ESCALA CORRETA
    
    PROBLEMA DETECTADO (conforme análise do professor):
    - Pesos de 10.000 destroem o gradiente
    - AG não percebe melhorias de 2-10 km (típicas de mutação)
    - Diferenças de 0.02% no fitness são invisíveis
    - População converge prematuramente
    
    SOLUÇÃO:
    - Escala lexicográfica: D = 1.000.000, R = 1.000, T = 1
    - Garante que 100m de distância > TODOS os componentes secundários
    - Gradiente suave e perceptível
    
    HIERARQUIA LEXICOGRÁFICA:
    1. DISTÂNCIA (×1.000.000) - Dominante absoluto
    2. POUSOS (×1.000) - Desempate médio
    3. TEMPO (×1) - Desempate fino
    4. PENALIDADES (×100.000.000) - Violações graves
    """
    try:
        # Simulação (rápida ou detalhada conforme Config)
        if Config.USE_FAST_FITNESS:
            distancia_total, tempo_total_seg, pousos, dias_usados, penalidade_vento = simular_rapido_simples(
                cromossomo, coords, dist_matrix, wind_cache
            )
        else:
            distancia_total, tempo_total_seg, pousos, dias_usados, penalidade_vento = simular_rapido(
                cromossomo, coords, dist_matrix, wind_cache
            )
        
        if distancia_total == float('inf'):
            return float('inf')
        
        # Componentes do fitness (escala lexicográfica)
        custo_distancia = distancia_total * Config.MULT_DISTANCIA
        custo_pousos = pousos * Config.MULT_POUSOS
        custo_tempo = tempo_total_seg * Config.MULT_TEMPO
        
        # Penalidades
        penalidade_total = 0.0
        
        if dias_usados > Config.PRAZO_DIAS:
            dias_excedidos = dias_usados - Config.PRAZO_DIAS
            penalidade_total += dias_excedidos * Config.PENALIDADE_DIAS
        
        if pousos > Config.POUSOS_LIMITE:
            pousos_excesso = pousos - Config.POUSOS_LIMITE
            penalidade_total += pousos_excesso * Config.PENALIDADE_POUSOS_EXCESSO
        
        if penalidade_vento > 0:
            penalidade_total += penalidade_vento * Config.PENALIDADE_VENTO
        
        # FITNESS FINAL (lexicográfico)
        fitness_final = custo_distancia + custo_pousos + custo_tempo + penalidade_total
        
        return fitness_final
        
    except Exception as e:
        print(f"Erro no fitness: {e}")
        return float('inf')


# ===========================
# SIMULAÇÃO SIMPLIFICADA E RÁPIDA
# ===========================
def simular_rapido_simples(cromossomo: Dict, coords: List[Tuple[float,float]],
                           dist_matrix: List[List[float]], wind_cache: Dict) -> Tuple[float, float, int, int, float]:
    """
    SIMULAÇÃO SIMPLIFICADA E RÁPIDA
    
    PROBLEMA: Simulação realista com física é MUITO lenta
    SOLUÇÃO: Estimativa rápida para fitness, detalhes apenas no final
    
    Elimina:
    - Física detalhada (aceleração/desaceleração)
    - Vento detalhado (usa estimativa simples)
    - Cálculo de horários exatos
    
    Mantém:
    - Distância exata
    - Estimativa de tempo (distância / velocidade média)
    - Estimativa de pousos (baseada em autonomia)
    - Dias estimados
    """
    rota = cromossomo['rota']
    velocidades = cromossomo['velocidades']
    
    # 1. DISTÂNCIA TOTAL (EXATA)
    distancia_total = 0.0
    for i in range(len(rota) - 1):
        idx_atual = rota[i]
        idx_prox = rota[i + 1]
        distancia_total += dist_matrix[idx_atual][idx_prox]
    
    # 2. TEMPO ESTIMADO (RÁPIDO)
    tempo_total_seg = 0.0
    
    for i in range(len(rota) - 1):
        idx_atual = rota[i]
        idx_prox = rota[i + 1]
        dist_km = dist_matrix[idx_atual][idx_prox]
        vel_kmh = velocidades[i]
        
        # Tempo básico: distância / velocidade
        tempo_voo = (dist_km / vel_kmh) * 3600  # segundos
        
        # Adiciona tempo de parada (se não for primeiro trecho)
        if i > 0:
            tempo_voo += Config.TEMPO_PARADA_SEG
        
        tempo_total_seg += tempo_voo
    
    # 3. POUSOS ESTIMADOS (BASEADO EM AUTONOMIA)
    bateria_restante = Config.AUTONOMIA_BASE_SEG
    pousos = 0
    
    for i in range(len(rota) - 1):
        idx_atual = rota[i]
        idx_prox = rota[i + 1]
        dist_km = dist_matrix[idx_atual][idx_prox]
        vel_kmh = velocidades[i]
        
        # Estimativa de consumo (proporcional à velocidade^1.5)
        velocidade_ref = 36.0
        fator_consumo = (vel_kmh / velocidade_ref) ** 1.5
        tempo_estimado = (dist_km / vel_kmh) * 3600
        consumo_estimado = tempo_estimado * fator_consumo
        
        # Verifica se precisa recarregar
        if bateria_restante < consumo_estimado * 1.2:  # Margem de segurança 20%
            pousos += 1
            bateria_restante = Config.AUTONOMIA_BASE_SEG
            tempo_total_seg += Config.TEMPO_RECARGA_SEG + Config.TEMPO_PARADA_SEG
        
        bateria_restante -= consumo_estimado
    
    # 4. DIAS ESTIMADOS
    horas_por_dia = Config.HORA_FIM - Config.HORA_INICIO  # 13 horas
    segundos_por_dia = horas_por_dia * 3600
    
    dias_usados = max(1, int(tempo_total_seg / segundos_por_dia) + 1)
    
    # 5. PENALIDADE VENTO (SIMPLIFICADA)
    penalidade_vento = 0.0
    
    return distancia_total, tempo_total_seg, pousos, dias_usados, penalidade_vento


# ===========================
# SIMULAÇÃO REALISTA COMPLETA
# ===========================
def simular_rapido(cromossomo: Dict, coords: List[Tuple[float,float]],
                   dist_matrix: List[List[float]], wind_cache: Dict) -> Tuple[float, float, int, int, float]:
    """
    SIMULAÇÃO RÁPIDA COM FÍSICA REALISTA
    
    Usado quando Config.USE_FAST_FITNESS = False
    Mais precisa que simular_rapido_simples, mas mais lenta
    """
    rota = cromossomo['rota']
    velocidades = cromossomo['velocidades']
    
    bateria_seg = Config.AUTONOMIA_BASE_SEG
    total_pousos = 0
    distancia_total = 0.0
    penalidade_vento = 0.0
    
    dt_atual = datetime(2025, 1, 1, Config.HORA_INICIO, 0, 0)
    tempo_total_seg = 0.0
    velocidade_atual_kmh = 0.0
    
    for idx in range(len(rota) - 1):
        i = rota[idx]
        j = rota[idx + 1]
        v_cruzeiro = velocidades[idx]
        dist_km = dist_matrix[i][j]
        distancia_total += dist_km
        
        # Tempo de parada (exceto primeiro)
        if idx > 0:
            tempo_total_seg += Config.TEMPO_PARADA_SEG
        
        # Verifica necessidade de recarga
        consumo_estimado = DronePhysics.estimar_consumo_trecho(dist_km, v_cruzeiro)
        
        if bateria_seg < 0:
            return float('inf'), float('inf'), 999, 999, float('inf')
        
        # Pouso para recarga
        if bateria_seg < consumo_estimado:
            total_pousos += 1
            tempo_total_seg += Config.TEMPO_RECARGA_SEG + Config.TEMPO_PARADA_SEG
            bateria_seg = Config.AUTONOMIA_BASE_SEG
            velocidade_atual_kmh = 0.0
        
        # Ajusta horário
        dt_atual = datetime(2025, 1, 1, Config.HORA_INICIO, 0, 0) + timedelta(seconds=int(tempo_total_seg))
        
        # Pouso por fim de dia
        if dt_atual.hour >= Config.HORA_FIM:
            dt_proximo_dia = (dt_atual + timedelta(days=1)).replace(
                hour=Config.HORA_INICIO, minute=0, second=0
            )
            tempo_espera = (dt_proximo_dia - dt_atual).total_seconds()
            tempo_total_seg += tempo_espera
            dt_atual = dt_proximo_dia
            velocidade_atual_kmh = 0.0
        
        # Obtém vento
        vento_kmh, dir_vento = get_wind_slot(dt_atual, wind_cache)
        dir_drone = bearing(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
        
        # Simula trecho
        tempo_voo_seg, consumo_seg, velocidade_final = DronePhysics.simular_trecho_com_fisica(
            dist_km=dist_km,
            v_inicial_kmh=velocidade_atual_kmh,
            v_cruzeiro_kmh=v_cruzeiro,
            vento_kmh=vento_kmh,
            dir_drone_graus=dir_drone,
            dir_vento_graus=dir_vento
        )
        
        velocidade_atual_kmh = velocidade_final
        
        # Penalidade vento
        v_efetiva = DronePhysics.calcular_velocidade_com_vento(
            v_cruzeiro / 3.6, dir_drone, vento_kmh, dir_vento
        ) * 3.6
        
        if v_efetiva < v_cruzeiro * 0.7:
            penalidade_vento += (v_cruzeiro - v_efetiva) * 0.5
        
        tempo_total_seg += tempo_voo_seg
        bateria_seg -= consumo_seg
        
        if bateria_seg < 0:
            return float('inf'), float('inf'), 999, 999, float('inf')
    
    tempo_inicial = datetime(2025, 1, 1, Config.HORA_INICIO, 0, 0)
    tempo_final = datetime(2025, 1, 1, Config.HORA_INICIO, 0, 0) + timedelta(seconds=int(tempo_total_seg))
    dias_usados = (tempo_final - tempo_inicial).days + 1
    
    return distancia_total, tempo_total_seg, total_pousos, dias_usados, penalidade_vento


# ===========================
# SIMULAÇÃO DETALHADA (PARA CSV)
# ===========================
def simulate_route_detailed(cromossomo: Dict, ceps: List[str],
                     coords: List[Tuple[float,float]],
                     dist_matrix: List[List[float]],
                     wind_cache: Dict) -> Tuple[List[Dict], Dict]:
    """
    Simulação detalhada para gerar CSV de saída
    Usa física realista completa
    """
    rota = cromossomo['rota']
    velocidades = cromossomo['velocidades']
    
    csv_rows = []
    bateria_seg = Config.AUTONOMIA_BASE_SEG
    
    total_pousos = 0
    total_pousos_tardios = 0
    custo_total_reais = 0.0
    distancia_total = 0.0
    
    dt_atual = datetime(2025, 1, 1, Config.HORA_INICIO, 0, 0)
    velocidade_atual_kmh = 0.0
    
    for idx in range(len(rota) - 1):
        i = rota[idx]
        j = rota[idx + 1]
        v_cruzeiro = velocidades[idx]
        dist_km = dist_matrix[i][j]
        distancia_total += dist_km
        
        # Tempo de parada
        if idx > 0:
            dt_atual += timedelta(seconds=Config.TEMPO_PARADA_SEG)
        
        consumo_estimado = DronePhysics.estimar_consumo_trecho(dist_km, v_cruzeiro)
        
        houve_pouso = False
        pouso_tardio = False
        
        # Pouso para recarga
        if bateria_seg < consumo_estimado:
            houve_pouso = True
            total_pousos += 1
            
            if dt_atual.hour >= Config.HORA_CUSTO_EXTRA:
                pouso_tardio = True
                total_pousos_tardios += 1
                custo_total_reais += Config.CUSTO_POUSO_REAIS + Config.CUSTO_POUSO_TARDIO
            else:
                custo_total_reais += Config.CUSTO_POUSO_REAIS
            
            dt_atual += timedelta(seconds=Config.TEMPO_RECARGA_SEG + Config.TEMPO_PARADA_SEG)
            bateria_seg = Config.AUTONOMIA_BASE_SEG
            velocidade_atual_kmh = 0.0
        
        # Pouso por fim de dia
        if dt_atual.hour >= Config.HORA_FIM:
            dt_atual = (dt_atual + timedelta(days=1)).replace(
                hour=Config.HORA_INICIO, minute=0, second=0
            )
            velocidade_atual_kmh = 0.0
        
        hora_inicial = dt_atual
        dia_semana = calcular_dia_semana(hora_inicial)
        
        vento_kmh, dir_vento = get_wind_slot(hora_inicial, wind_cache)
        dir_drone = bearing(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
        
        tempo_voo_seg, consumo_seg, velocidade_final = DronePhysics.simular_trecho_com_fisica(
            dist_km=dist_km,
            v_inicial_kmh=velocidade_atual_kmh,
            v_cruzeiro_kmh=v_cruzeiro,
            vento_kmh=vento_kmh,
            dir_drone_graus=dir_drone,
            dir_vento_graus=dir_vento
        )
        
        velocidade_atual_kmh = velocidade_final
        hora_final = hora_inicial + timedelta(seconds=tempo_voo_seg)
        
        if hora_final.hour >= Config.HORA_FIM:
            fim_operacao = hora_final.replace(hour=Config.HORA_FIM, minute=0, second=0)
            if hora_final > fim_operacao:
                tempo_excedente = (hora_final - fim_operacao).total_seconds()
                hora_final = (fim_operacao + timedelta(days=1)).replace(
                    hour=Config.HORA_INICIO, minute=0, second=0
                )
                hora_final += timedelta(seconds=tempo_excedente)
        
        bateria_seg -= consumo_seg
        
        csv_rows.append({
            "cep_inicial": ceps[i],
            "lat_inicial": f"{coords[i][0]:.10f}",
            "lon_inicial": f"{coords[i][1]:.10f}",
            "dia": dia_semana,
            "hora_inicial": hora_inicial.strftime("%H:%M:%S"),
            "velocidade": v_cruzeiro,
            "cep_final": ceps[j],
            "lat_final": f"{coords[j][0]:.10f}",
            "lon_final": f"{coords[j][1]:.10f}",
            "pouso": "SIM" if houve_pouso else "NÃO",
            "hora_final": hora_final.strftime("%H:%M:%S")
        })
        
        dt_atual = hora_final
    
    tempo_final = dt_atual
    tempo_inicial = datetime(2025, 1, 1, Config.HORA_INICIO, 0, 0)
    tempo_total_seg = (tempo_final - tempo_inicial).total_seconds()
    
    metricas = {
        'tempo_total_seg': tempo_total_seg,
        'distancia_total_km': distancia_total,
        'pousos': total_pousos,
        'pousos_tardios': total_pousos_tardios,
        'custo_reais': custo_total_reais,
        'dias_usados': (tempo_final - tempo_inicial).days + 1
    }
    
    return csv_rows, metricas


# ===========================
# VALIDAÇÕES
# ===========================
def validate_solution(csv_rows: List[Dict], ceps: List[str]) -> Dict:
    """Valida COMPLETAMENTE a solução"""
    resultados = {}
    
    # 1. Todos os CEPs visitados?
    ceps_visitados = set()
    for row in csv_rows:
        ceps_visitados.add(row['cep_inicial'])
        ceps_visitados.add(row['cep_final'])
    
    ceps_esperados = set(ceps)
    resultados['todos_ceps'] = (ceps_visitados == ceps_esperados)
    resultados['ceps_faltando'] = list(ceps_esperados - ceps_visitados)
    
    # 2. Inicia e termina na Unibrasil?
    resultados['inicio_correto'] = (csv_rows[0]['cep_inicial'] == Config.CEP_UNIBRASIL)
    resultados['fim_correto'] = (csv_rows[-1]['cep_final'] == Config.CEP_UNIBRASIL)
    
    # 3. Velocidades válidas?
    velocidades_invalidas = []
    for idx, row in enumerate(csv_rows):
        vel = row['velocidade']
        if vel < Config.VELOCIDADE_MINIMA or vel > Config.VELOCIDADE_MAXIMA:
            velocidades_invalidas.append((idx, vel, 'fora_range'))
        if vel % Config.MULTIPLO_VELOCIDADE != 0:
            velocidades_invalidas.append((idx, vel, 'nao_multiplo_4'))
    
    resultados['velocidades_validas'] = (len(velocidades_invalidas) == 0)
    resultados['velocidades_invalidas'] = velocidades_invalidas
    
    # 4. Horários válidos?
    horarios_invalidos = []
    for idx, row in enumerate(csv_rows):
        h_ini = datetime.strptime(row['hora_inicial'], "%H:%M:%S").hour
        h_fim = datetime.strptime(row['hora_final'], "%H:%M:%S").hour
        
        if h_ini < Config.HORA_INICIO or h_ini >= Config.HORA_FIM:
            horarios_invalidos.append((idx, 'inicial', row['hora_inicial']))
        if h_fim < Config.HORA_INICIO or h_fim > Config.HORA_FIM:
            horarios_invalidos.append((idx, 'final', row['hora_final']))
    
    resultados['horarios_validos'] = (len(horarios_invalidos) == 0)
    resultados['horarios_invalidos'] = horarios_invalidos
    
    # 5. Dentro do prazo?
    dias_usados = set(row['dia'] for row in csv_rows)
    resultados['dentro_prazo'] = (max(dias_usados) <= Config.PRAZO_DIAS)
    resultados['dias_usados'] = max(dias_usados)
    
    return resultados