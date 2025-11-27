# physics.py
import math
from typing import Tuple

class DronePhysics:
    """
    Motor de física realista para simulação de voo do drone.
    
    IMPORTANTE: O drone sempre inicia de velocidade 0 km/h e precisa
    acelerar/desacelerar gradualmente.
    
    Baseado nas especificações do PDF e orientações do professor.
    """
    
    # Constantes físicas (conforme PDF)
    ACELERACAO = 2.0  # m/s² (aceleração)
    DESACELERACAO = 3.0  # m/s² (desaceleração - freio mais eficiente)
    
    # Velocidade de referência (mais eficiente energeticamente)
    VELOCIDADE_REFERENCIA_KMH = 36.0  # 10 m/s
    
    @staticmethod
    def simular_trecho_com_fisica(dist_km: float, 
                                   v_inicial_kmh: float, 
                                   v_cruzeiro_kmh: float,
                                   vento_kmh: float = 0.0,
                                   dir_drone_graus: float = 0.0,
                                   dir_vento_graus: float = 0.0) -> Tuple[float, float, float]:
        """
        Simula um trecho de voo com física REALISTA.
        
        O trecho é dividido em 3 fases:
        1. ACELERAÇÃO: v_inicial → v_cruzeiro
        2. CRUZEIRO: v_cruzeiro constante
        3. DESACELERAÇÃO: v_cruzeiro → 0
        
        Args:
            dist_km: Distância do trecho em km
            v_inicial_kmh: Velocidade inicial em km/h (normalmente 0)
            v_cruzeiro_kmh: Velocidade de cruzeiro desejada em km/h
            vento_kmh: Velocidade do vento em km/h
            dir_drone_graus: Direção do drone em graus (0-360)
            dir_vento_graus: Direção do vento em graus (0-360)
        
        Returns:
            (tempo_total_seg, consumo_bateria_seg, velocidade_final_kmh)
        """
        
        # Conversões
        v_inicial_ms = v_inicial_kmh / 3.6
        v_cruzeiro_ms = v_cruzeiro_kmh / 3.6
        dist_m = dist_km * 1000.0
        
        # Calcula velocidade efetiva com vento
        v_efetiva_ms = DronePhysics.calcular_velocidade_com_vento(
            v_cruzeiro_ms, dir_drone_graus, vento_kmh, dir_vento_graus
        )
        
        # === FASE 1: ACELERAÇÃO (v_inicial → v_cruzeiro) ===
        if v_inicial_ms < v_cruzeiro_ms:
            # Tempo para acelerar: t = (v_final - v_inicial) / a
            tempo_acel = (v_cruzeiro_ms - v_inicial_ms) / DronePhysics.ACELERACAO
            
            # Distância percorrida: d = v_inicial*t + 0.5*a*t²
            dist_acel = v_inicial_ms * tempo_acel + 0.5 * DronePhysics.ACELERACAO * tempo_acel**2
            
            # Consumo na aceleração (proporcional ao tempo)
            consumo_acel = tempo_acel
        else:
            tempo_acel = 0.0
            dist_acel = 0.0
            consumo_acel = 0.0
        
        # === FASE 3: DESACELERAÇÃO (v_cruzeiro → 0) ===
        # Tempo para desacelerar: t = v / a
        tempo_desacel = v_cruzeiro_ms / DronePhysics.DESACELERACAO
        
        # Distância percorrida: d = v*t - 0.5*a*t²
        dist_desacel = v_cruzeiro_ms * tempo_desacel - 0.5 * DronePhysics.DESACELERACAO * tempo_desacel**2
        
        # Consumo na desaceleração
        consumo_desacel = tempo_desacel
        
        # === FASE 2: CRUZEIRO (velocidade constante) ===
        dist_cruzeiro = dist_m - dist_acel - dist_desacel
        
        # Se a distância é muito curta e não há espaço para cruzeiro
        if dist_cruzeiro < 0:
            # Recalcula: drone acelera até uma velocidade intermediária e desacelera
            # v_max² = v_inicial² + 2*a*d_total (simplificado)
            # Para simplificar, usamos velocidade média
            v_max_possivel_ms = math.sqrt(
                v_inicial_ms**2 + 2 * DronePhysics.ACELERACAO * dist_m / 2
            )
            
            if v_max_possivel_ms > v_cruzeiro_ms:
                v_max_possivel_ms = v_cruzeiro_ms
            
            tempo_acel = (v_max_possivel_ms - v_inicial_ms) / DronePhysics.ACELERACAO
            dist_acel = v_inicial_ms * tempo_acel + 0.5 * DronePhysics.ACELERACAO * tempo_acel**2
            
            tempo_desacel = v_max_possivel_ms / DronePhysics.DESACELERACAO
            dist_desacel = v_max_possivel_ms * tempo_desacel - 0.5 * DronePhysics.DESACELERACAO * tempo_desacel**2
            
            tempo_cruzeiro = 0.0
            consumo_cruzeiro = 0.0
            
            consumo_acel = tempo_acel
            consumo_desacel = tempo_desacel
        else:
            # Tempo em cruzeiro: t = d / v
            tempo_cruzeiro = dist_cruzeiro / v_efetiva_ms if v_efetiva_ms > 0 else 0.0
            
            # Consumo no cruzeiro (baseado na fórmula do PDF)
            # Consumo aumenta com o quadrado da velocidade relativa à velocidade de referência
            fator_consumo = (v_cruzeiro_kmh / DronePhysics.VELOCIDADE_REFERENCIA_KMH) ** 2
            consumo_cruzeiro = tempo_cruzeiro * fator_consumo
        
        # === TOTAIS ===
        tempo_total = tempo_acel + tempo_cruzeiro + tempo_desacel
        consumo_total = consumo_acel + consumo_cruzeiro + consumo_desacel
        
        # Velocidade final: sempre 0 após desaceleração
        velocidade_final_kmh = 0.0
        
        return tempo_total, consumo_total, velocidade_final_kmh
    
    @staticmethod
    def estimar_consumo_trecho(dist_km: float, v_cruzeiro_kmh: float) -> float:
        """
        Estimativa RÁPIDA do consumo de bateria para um trecho.
        
        Usado para verificar se há bateria suficiente ANTES de iniciar o voo.
        
        Args:
            dist_km: Distância em km
            v_cruzeiro_kmh: Velocidade de cruzeiro em km/h
        
        Returns:
            Consumo estimado em segundos de bateria
        """
        v_cruzeiro_ms = v_cruzeiro_kmh / 3.6
        dist_m = dist_km * 1000.0
        
        # Estimativa simplificada: considera aceleração + cruzeiro + desaceleração
        # Usa uma margem de segurança de 30%
        
        # Tempo básico de cruzeiro
        tempo_base = (dist_km / v_cruzeiro_kmh) * 3600  # segundos
        
        # Fator de consumo baseado na velocidade
        fator_consumo = (v_cruzeiro_kmh / DronePhysics.VELOCIDADE_REFERENCIA_KMH) ** 2
        
        # Aplica margem de segurança
        consumo_estimado = tempo_base * fator_consumo * 1.3
        
        return consumo_estimado
    
    @staticmethod
    def calcular_velocidade_com_vento(v_drone_ms: float, 
                                       dir_drone_graus: float,
                                       vento_kmh: float,
                                       dir_vento_graus: float) -> float:
        """
        Calcula a velocidade efetiva do drone considerando o vento.
        
        Baseado no exemplo do ChatGPT fornecido no PDF:
        - Vento a favor: aumenta velocidade
        - Vento contrário: reduz velocidade
        - Vento lateral: componente vetorial
        
        Args:
            v_drone_ms: Velocidade do drone em m/s
            dir_drone_graus: Direção do drone (0-360°, 0=Norte)
            vento_kmh: Velocidade do vento em km/h
            dir_vento_graus: Direção do vento (0-360°, 0=Norte)
        
        Returns:
            Velocidade efetiva em m/s
        """
        if vento_kmh == 0:
            return v_drone_ms
        
        # Converte vento para m/s
        vento_ms = vento_kmh / 3.6
        
        # Calcula ângulo relativo entre drone e vento
        # Se vento vem de SSE (157.5°) e drone vai para NE (45°), ângulo = 112.5°
        angulo_relativo = abs(dir_drone_graus - dir_vento_graus)
        if angulo_relativo > 180:
            angulo_relativo = 360 - angulo_relativo
        
        # Componente do vento na direção do movimento do drone
        # Vento a favor (0°): cos(0) = 1 → velocidade aumenta
        # Vento contrário (180°): cos(180) = -1 → velocidade diminui
        # Vento lateral (90°): cos(90) = 0 → sem efeito direto
        componente_vento = vento_ms * math.cos(math.radians(angulo_relativo))
        
        # Velocidade efetiva
        v_efetiva = v_drone_ms + componente_vento
        
        # Garante que velocidade não seja negativa
        if v_efetiva < 0:
            v_efetiva = 0.1  # Velocidade mínima para evitar divisão por zero
        
        return v_efetiva

def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula o bearing (direção) de um ponto para outro em graus.
    
    Args:
        lat1, lon1: Coordenadas do ponto inicial (graus)
        lat2, lon2: Coordenadas do ponto final (graus)
    
    Returns:
        Bearing em graus (0-360, 0=Norte, 90=Leste)
    """
    # Converte para radianos
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δλ = math.radians(lon2 - lon1)
    
    # Calcula bearing
    x = math.sin(Δλ) * math.cos(φ2)
    y = math.cos(φ1) * math.sin(φ2) - math.sin(φ1) * math.cos(φ2) * math.cos(Δλ)
    
    θ = math.atan2(x, y)
    
    # Converte para graus e normaliza para 0-360
    bearing_graus = (math.degrees(θ) + 360) % 360
    
    return bearing_graus


# ===========================
# EXEMPLO DE USO
# ===========================
if __name__ == "__main__":
    print("="*70)
    print(" TESTE DO MOTOR DE FÍSICA DO DRONE")
    print("="*70)
    
    # Teste 1: Voo de 2 km a 72 km/h sem vento
    print("\nTeste 1: 2 km a 72 km/h (sem vento)")
    print("-" * 70)
    
    dist_km = 2.0
    v_inicial = 0.0  # Sempre começa parado
    v_cruzeiro = 72.0
    
    tempo, consumo, v_final = DronePhysics.simular_trecho_com_fisica(
        dist_km, v_inicial, v_cruzeiro
    )
    
    print(f"Distância: {dist_km} km")
    print(f"Velocidade inicial: {v_inicial} km/h")
    print(f"Velocidade de cruzeiro: {v_cruzeiro} km/h")
    print(f"Tempo total: {tempo:.1f} segundos ({tempo/60:.2f} minutos)")
    print(f"Consumo de bateria: {consumo:.1f} segundos")
    print(f"Velocidade final: {v_final} km/h")
    
    # Teste 2: Mesmo voo com vento contrário
    print("\n\nTeste 2: 2 km a 72 km/h (vento contrário 9 km/h)")
    print("-" * 70)
    
    tempo2, consumo2, v_final2 = DronePhysics.simular_trecho_com_fisica(
        dist_km, v_inicial, v_cruzeiro,
        vento_kmh=9.0,
        dir_drone_graus=39.5,
        dir_vento_graus=157.5  # SSE
    )
    
    print(f"Tempo total: {tempo2:.1f} segundos ({tempo2/60:.2f} minutos)")
    print(f"Consumo de bateria: {consumo2:.1f} segundos")
    print(f"Diferença de tempo: +{tempo2-tempo:.1f} segundos")
    
    # Teste 3: Estimativa rápida
    print("\n\nTeste 3: Estimativa de consumo (verificação antes do voo)")
    print("-" * 70)
    
    consumo_estimado = DronePhysics.estimar_consumo_trecho(dist_km, v_cruzeiro)
    print(f"Consumo estimado: {consumo_estimado:.1f} segundos")
    print(f"Consumo real (teste 1): {consumo:.1f} segundos")
    print(f"Margem de segurança: {((consumo_estimado - consumo) / consumo * 100):.1f}%")
    
    # Teste 4: Bearing
    print("\n\nTeste 4: Cálculo de direção (bearing)")
    print("-" * 70)
    
    lat1, lon1 = -25.4524871, -49.2925963  # Unibrasil
    lat2, lon2 = -25.4376831, -49.2729254  # Outro ponto
    
    dir_voo = bearing(lat1, lon1, lat2, lon2)
    print(f"De ({lat1}, {lon1})")
    print(f"Para ({lat2}, {lon2})")
    print(f"Direção: {dir_voo:.1f}° (0°=Norte, 90°=Leste)")
    
    print("\n" + "="*70)
    print(" TESTES CONCLUÍDOS")
    print("="*70)
