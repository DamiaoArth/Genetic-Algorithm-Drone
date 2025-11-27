import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
from typing import List, Tuple, Dict

def plotar_distribuicao_ventos(wind_schedule: Dict, salvar_em: str = "distribuicao_ventos.png"):
    """
    Plota distribuição dos ventos conforme especificação do PDF
    
    Gera 2 gráficos:
    1. Velocidade do vento por dia/horário
    2. Direção do vento (rosa dos ventos) por dia/horário
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Distribuição dos Ventos - 7 Dias de Previsão', 
                 fontsize=16, fontweight='bold')
    
    # Prepara dados
    dias = sorted([int(d) for d in wind_schedule.keys()])
    horarios = [6, 9, 12, 15, 18]
    
    # ========================================
    # GRÁFICO 1: Velocidade do Vento
    # ========================================
    velocidades_por_horario = {h: [] for h in horarios}
    
    for dia in dias:
        dia_str = str(dia)
        for hora in horarios:
            hora_str = str(hora)
            vel = wind_schedule[dia_str][hora_str]['velocidade_kmh']
            velocidades_por_horario[hora].append(vel)
    
    # Plota linhas para cada horário
    cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for idx, hora in enumerate(horarios):
        ax1.plot(dias, velocidades_por_horario[hora], 
                marker='o', linewidth=2, markersize=8,
                label=f'{hora:02d}:00h', color=cores[idx])
    
    ax1.set_xlabel('Dia', fontsize=12)
    ax1.set_ylabel('Velocidade do Vento (km/h)', fontsize=12)
    ax1.set_title('Velocidade do Vento por Dia e Horário', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(dias)
    ax1.set_ylim(0, max([max(v) for v in velocidades_por_horario.values()]) + 3)
    
    # ========================================
    # GRÁFICO 2: Rosa dos Ventos (Direção)
    # ========================================
    # Converte para coordenadas polares
    ax2 = plt.subplot(122, projection='polar')
    
    # Para cada dia, plota direção média do vento
    for dia in dias:
        dia_str = str(dia)
        direcoes = []
        velocidades = []
        
        for hora in horarios:
            hora_str = str(hora)
            dir_graus = wind_schedule[dia_str][hora_str]['direcao_graus']
            vel = wind_schedule[dia_str][hora_str]['velocidade_kmh']
            
            # Converte graus para radianos (0° = Norte, sentido horário)
            # Matplotlib polar usa 0 = Leste, sentido anti-horário
            # Então precisamos converter: θ_polar = 90° - θ_meteorológico
            dir_rad = np.radians(90 - dir_graus)
            
            direcoes.append(dir_rad)
            velocidades.append(vel)
        
        # Plota como scatter com tamanho proporcional à velocidade
        ax2.scatter(direcoes, velocidades, 
                   s=[v*20 for v in velocidades],
                   alpha=0.6, label=f'Dia {dia}',
                   marker='o')
    
    # Configura eixos
    ax2.set_theta_zero_location('N')  # 0° = Norte
    ax2.set_theta_direction(-1)  # Sentido horário
    ax2.set_title('Direção e Intensidade do Vento\n(tamanho = velocidade)', 
                 fontsize=13, fontweight='bold', pad=20)
    ax2.set_ylim(0, 25)
    ax2.set_yticks([5, 10, 15, 20])
    ax2.set_yticklabels(['5 km/h', '10', '15', '20'])
    ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
    
    # Adiciona rótulos dos pontos cardeais
    ax2.text(np.radians(0), 26, 'N', ha='center', va='center', fontsize=14, fontweight='bold')
    ax2.text(np.radians(90), 26, 'L', ha='center', va='center', fontsize=14, fontweight='bold')
    ax2.text(np.radians(180), 26, 'S', ha='center', va='center', fontsize=14, fontweight='bold')
    ax2.text(np.radians(270), 26, 'O', ha='center', va='center', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(salvar_em, dpi=300, bbox_inches='tight')
    print(f"\n✓ Gráfico de ventos salvo em: {salvar_em}")


def plotar_mapa_rota(csv_rows: List[Dict], ceps: List[str], coords: List[Tuple[float, float]], 
                     idx_unibrasil: int, salvar_em: str = "mapa_rota.png"):
    """
    Plota mapa da rota percorrida (Latitude x Longitude)
    Conforme exemplo do PDF com ponto vermelho na Unibrasil
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # ========================================
    # EXTRAI COORDENADAS DA ROTA
    # ========================================
    rota_lats = []
    rota_lons = []
    
    # Ponto inicial (Unibrasil)
    rota_lats.append(coords[idx_unibrasil][0])
    rota_lons.append(coords[idx_unibrasil][1])
    
    # Pontos intermediários
    for row in csv_rows:
        lat_final = float(row['lat_final'])
        lon_final = float(row['lon_final'])
        rota_lats.append(lat_final)
        rota_lons.append(lon_final)
    
    # ========================================
    # PLOTA TODOS OS CEPS (PONTOS CINZA CLARO)
    # ========================================
    todas_lats = [c[0] for c in coords]
    todas_lons = [c[1] for c in coords]
    
    ax.scatter(todas_lons, todas_lats, 
              c='lightgray', s=50, alpha=0.5, 
              marker='o', label='Todos os CEPs', zorder=1)
    
    # ========================================
    # PLOTA A ROTA (LINHA AZUL)
    # ========================================
    ax.plot(rota_lons, rota_lats, 
           'b-', linewidth=2, alpha=0.6, 
           label='Rota do Drone', zorder=2)
    
    # ========================================
    # PLOTA PONTOS VISITADOS (CÍRCULOS AZUIS)
    # ========================================
    ax.scatter(rota_lons[1:-1], rota_lats[1:-1], 
              c='blue', s=80, alpha=0.7, 
              marker='o', edgecolors='darkblue', linewidths=1.5,
              label='CEPs Visitados', zorder=3)
    
    # ========================================
    # DESTACA UNIBRASIL (PONTO VERMELHO)
    # ========================================
    ax.scatter(coords[idx_unibrasil][1], coords[idx_unibrasil][0], 
              c='red', s=300, alpha=0.9, 
              marker='*', edgecolors='darkred', linewidths=2,
              label='Unibrasil (Início/Fim)', zorder=4)
    
    # ========================================
    # ADICIONA SETAS DE DIREÇÃO
    # ========================================
    # Adiciona setas a cada 5 pontos para mostrar direção
    for i in range(0, len(rota_lons)-1, 5):
        dx = rota_lons[i+1] - rota_lons[i]
        dy = rota_lats[i+1] - rota_lats[i]
        
        ax.arrow(rota_lons[i], rota_lats[i], 
                dx*0.3, dy*0.3,
                head_width=0.001, head_length=0.001,
                fc='darkblue', ec='darkblue', alpha=0.5, zorder=2)
    
    # ========================================
    # CONFIGURAÇÕES DO GRÁFICO
    # ========================================
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Mapa da Rota do Drone - Curitiba\n(Percurso Otimizado pelo AG)', 
                fontsize=14, fontweight='bold', pad=15)
    
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Adiciona estatísticas no gráfico
    num_ceps = len(rota_lons) - 1  # -1 porque início = fim
    distancia_total = sum([
        np.sqrt((rota_lons[i+1] - rota_lons[i])**2 + 
               (rota_lats[i+1] - rota_lats[i])**2)
        for i in range(len(rota_lons)-1)
    ]) * 111  # Aproximação: 1° ≈ 111 km
    
    texto_stats = f'Total de CEPs: {num_ceps}\nDistância aprox: {distancia_total:.1f} km'
    ax.text(0.02, 0.98, texto_stats, 
           transform=ax.transAxes, fontsize=10,
           verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Ajusta limites para dar margem
    margin = 0.01
    ax.set_xlim(min(todas_lons) - margin, max(todas_lons) + margin)
    ax.set_ylim(min(todas_lats) - margin, max(todas_lats) + margin)
    
    plt.tight_layout()
    plt.savefig(salvar_em, dpi=300, bbox_inches='tight')
    print(f"✓ Mapa da rota salvo em: {salvar_em}")


def plotar_estatisticas_rota(csv_rows: List[Dict], metricas: Dict, 
                             salvar_em: str = "estatisticas_rota.png"):
    """
    Plota estatísticas detalhadas da rota
    - Distribuição de pousos por dia
    - Distribuição de velocidades
    - Distribuição de horários de voo
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Estatísticas Detalhadas da Rota', fontsize=16, fontweight='bold')
    
    # ========================================
    # GRÁFICO 1: Pousos por Dia
    # ========================================
    ax1 = axes[0, 0]
    
    pousos_por_dia = {}
    for row in csv_rows:
        if row['pouso'] == 'SIM':
            dia = row['dia']
            pousos_por_dia[dia] = pousos_por_dia.get(dia, 0) + 1
    
    dias = sorted(pousos_por_dia.keys())
    pousos = [pousos_por_dia[d] for d in dias]
    
    bars = ax1.bar(dias, pousos, color='coral', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Dia', fontsize=11)
    ax1.set_ylabel('Número de Pousos', fontsize=11)
    ax1.set_title('Distribuição de Pousos por Dia', fontsize=12, fontweight='bold')
    ax1.set_xticks(range(1, 8))
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Adiciona valores nas barras
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # ========================================
    # GRÁFICO 2: Distribuição de Velocidades
    # ========================================
    ax2 = axes[0, 1]
    
    velocidades = [row['velocidade'] for row in csv_rows]
    
    ax2.hist(velocidades, bins=range(36, 100, 4), color='skyblue', 
            alpha=0.7, edgecolor='black')
    ax2.axvline(np.mean(velocidades), color='red', linestyle='--', 
               linewidth=2, label=f'Média: {np.mean(velocidades):.1f} km/h')
    ax2.set_xlabel('Velocidade (km/h)', fontsize=11)
    ax2.set_ylabel('Frequência', fontsize=11)
    ax2.set_title('Distribuição de Velocidades Utilizadas', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # ========================================
    # GRÁFICO 3: Horários de Voo (Timeline)
    # ========================================
    ax3 = axes[1, 0]
    
    from datetime import datetime
    
    horarios_inicio = []
    dias_voo = []
    
    for row in csv_rows:
        hora = datetime.strptime(row['hora_inicial'], '%H:%M:%S')
        horarios_inicio.append(hora.hour + hora.minute/60)
        dias_voo.append(row['dia'])
    
    scatter = ax3.scatter(horarios_inicio, dias_voo, 
                         c=dias_voo, cmap='viridis', s=50, alpha=0.6)
    ax3.set_xlabel('Hora do Dia', fontsize=11)
    ax3.set_ylabel('Dia', fontsize=11)
    ax3.set_title('Distribuição Temporal dos Voos', fontsize=12, fontweight='bold')
    ax3.set_xlim(6, 19)
    ax3.set_ylim(0.5, 7.5)
    ax3.set_xticks(range(6, 20, 2))
    ax3.set_yticks(range(1, 8))
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax3, label='Dia')
    
    # ========================================
    # GRÁFICO 4: Métricas Gerais
    # ========================================
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Texto com métricas
    texto_metricas = f"""
    MÉTRICAS GERAIS DA SOLUÇÃO
    
    Distância Total: {metricas['distancia_total_km']:.2f} km
    Tempo Total: {metricas['tempo_total_seg']/3600:.2f} horas
    
    Número de Pousos: {metricas['pousos']}
    Pousos Tardios: {metricas['pousos_tardios']}
    Custo de Pousos: R$ {metricas['custo_reais']:.2f}
    
    Dias Utilizados: {metricas['dias_usados']} / 7
    Prazo: {'✓ OK' if metricas['dias_usados'] <= 7 else '✗ EXCEDIDO'}
    
    Velocidade Média: {np.mean(velocidades):.1f} km/h
    Velocidade Mín: {min(velocidades)} km/h
    Velocidade Máx: {max(velocidades)} km/h
    """
    
    ax4.text(0.1, 0.5, texto_metricas, 
            fontsize=11, verticalalignment='center',
            family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig(salvar_em, dpi=300, bbox_inches='tight')
    print(f"✓ Estatísticas da rota salvas em: {salvar_em}")


def gerar_todos_graficos(csv_rows: List[Dict], ceps: List[str], 
                        coords: List[Tuple[float, float]], idx_unibrasil: int,
                        metricas: Dict, wind_schedule_path: str = None):
    """
    Gera TODOS os gráficos necessários conforme PDF
    """
    print("\n" + "="*80)
    print(" GERANDO GRÁFICOS CONFORME ESPECIFICAÇÃO DO PDF")
    print("="*80)
    
    # 1. Gráfico de ventos
    if wind_schedule_path:
        try:
            with open(wind_schedule_path, 'r', encoding='utf-8') as f:
                wind_schedule = json.load(f)
            plotar_distribuicao_ventos(wind_schedule, "distribuicao_ventos.png")
        except Exception as e:
            print(f"⚠ Não foi possível gerar gráfico de ventos: {e}")
    else:
        print("⚠ Arquivo de ventos não fornecido. Pulando gráfico de ventos.")
    
    # 2. Mapa da rota
    plotar_mapa_rota(csv_rows, ceps, coords, idx_unibrasil, "mapa_rota.png")
    
    # 3. Estatísticas da rota
    plotar_estatisticas_rota(csv_rows, metricas, "estatisticas_rota.png")
    
    print("="*80)
    print(" TODOS OS GRÁFICOS GERADOS COM SUCESSO!")
    print("="*80)
    print("\nArquivos gerados:")
    print("  1. distribuicao_ventos.png - Velocidade e direção dos ventos")
    print("  2. mapa_rota.png - Mapa da rota (lat x lon)")
    print("  3. estatisticas_rota.png - Estatísticas detalhadas")
    print("  4. monitoramento_completo.png - Evolução do AG (já existente)")
    print("  5. metricas_solucao.png - Métricas finais (já existente)")
    print("="*80 + "\n")


# ===========================
# EXEMPLO DE USO
# ===========================
if __name__ == "__main__":
    print("Este módulo deve ser importado e usado no main.py")
    print("\nExemplo de uso:")
    print("""
from visualizacao import gerar_todos_graficos

# Após executar o AG e obter a melhor solução:
gerar_todos_graficos(
    csv_rows=csv_rows,
    ceps=ceps,
    coords=coords,
    idx_unibrasil=idx_unibrasil,
    metricas=metricas,
    wind_schedule_path='previsao_ventos.json'
)
    """)