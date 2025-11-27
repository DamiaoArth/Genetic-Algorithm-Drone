#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIBRASIL SURVEYOR - Otimização de Rota de Drone
Sistema de planejamento de rotas para drone autônomo usando Algoritmo Genético

Autores: 
    Arthur Damiao Mendes - 2023102413
    Gabryel Zanella - 2023100930
    Luiz Felipe - 2023201245
Disciplina: Serviços Cognitivos
Professor: Mozart Hasse
Data: 2025
"""

import argparse
import random
import sys
import os
from pathlib import Path
from datetime import timedelta

# Adiciona diretório core ao path
sys.path.insert(0, str(Path(__file__).parent / 'core'))

import numpy as np
from core.config import Config
from core.data_loader import load_ceps_coords, generate_distance_matrix, build_wind_cache
from core.genetic_algorithm import evolve_optimized
from core.simulation import simulate_route_detailed, validate_solution

# ⚠️ CORREÇÃO PRINCIPAL: Import correto das funções de visualização
from core.visualization import (
    plotar_distribuicao_ventos,
    plotar_mapa_rota,
    plotar_estatisticas_rota
)

# Diretórios do projeto
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'

# Cria diretório de output se não existir
OUTPUT_DIR.mkdir(exist_ok=True)


def validar_arquivos_entrada(arquivo_ceps: str, arquivo_ventos: str = None):
    """
    Valida existência dos arquivos de entrada
    
    Args:
        arquivo_ceps: Nome do arquivo CSV com CEPs
        arquivo_ventos: Nome do arquivo JSON com ventos (opcional)
    
    Returns:
        Tuple[Path, Path]: Caminhos completos dos arquivos
    
    Raises:
        FileNotFoundError: Se arquivos obrigatórios não existirem
    """
    # Valida arquivo de CEPs
    path_ceps = DATA_DIR / arquivo_ceps
    if not path_ceps.exists():
        raise FileNotFoundError(
            f"Arquivo de CEPs não encontrado: {path_ceps}\n"
            f"Certifique-se de que o arquivo está em {DATA_DIR}/"
        )
    
    # Valida arquivo de ventos (opcional)
    path_ventos = None
    if arquivo_ventos:
        path_ventos = DATA_DIR / arquivo_ventos
        if not path_ventos.exists():
            print(f"⚠️  Aviso: Arquivo de ventos não encontrado: {path_ventos}")
            print(f"   Executando SEM considerar ventos (vento = 0)")
            path_ventos = None
    
    return path_ceps, path_ventos


def imprimir_cabecalho():
    """Imprime cabeçalho do programa"""
    print("\n" + "="*100)
    print(" UNIBRASIL SURVEYOR - Otimização de Rota de Drone ".center(100))
    print(" Algoritmo Genético para Planejamento de Rotas ".center(100))
    print("="*100)


def imprimir_configuracao(args, usa_ventos: bool):
    """Imprime configuração da execução"""
    print("\n⚙️  CONFIGURAÇÃO DA EXECUÇÃO:")
    print(f"   • Arquivo de entrada: {args.arquivo}")
    print(f"   • Arquivo de saída: {args.out}")
    print(f"   • Considerando ventos: {'SIM' if usa_ventos else 'NÃO'}")
    print(f"   • Seed: {args.seed if args.seed else 'Aleatória'}")
    
    print(f"\n📊 CONFIGURAÇÃO DO FITNESS:")
    print(f"   • Hierarquia: DISTÂNCIA (×{Config.MULT_DISTANCIA:,.0f}) >> "
          f"POUSOS (×{Config.MULT_POUSOS:,.0f}) >> "
          f"TEMPO (×{Config.MULT_TEMPO:,.0f})")
    
    print(f"\n🧬 CONFIGURAÇÃO DO ALGORITMO GENÉTICO:")
    print(f"   • População: {args.pop} indivíduos")
    print(f"   • Gerações: {args.gen}")
    print(f"   • Crossover: OX ({Config.CROSSOVER_RATE})")
    print(f"   • Mutação: Swap ({Config.MUTATION_RATE_SWAP}) + "
          f"Inversion ({Config.MUTATION_RATE_INVERSION}) + "
          f"2-opt ({Config.MUTATION_RATE_2OPT})")
    print(f"   • Elitismo: {Config.ELITISM_COUNT} indivíduos")
    print(f"   • Torneio: k={Config.TOURNAMENT_SIZE}")
    print(f"   • Simulação: {'RÁPIDA' if Config.USE_FAST_FITNESS else 'DETALHADA'}")


def carregar_dados(arquivo_ceps: Path, arquivo_ventos: Path = None):
    """
    Carrega todos os dados necessários
    
    Returns:
        Tuple com (ceps, coords, dist_matrix, idx_unibrasil, wind_cache, wind_schedule)
    """
    # Carrega CEPs e coordenadas
    print(f"\n📂 CARREGANDO DADOS...")
    print(f"   Arquivo: {arquivo_ceps}")
    
    ceps, coords, idx_unibrasil = load_ceps_coords(str(arquivo_ceps))
    
    print(f"   ✓ {len(ceps)} CEPs carregados")
    print(f"   ✓ Unibrasil (índice {idx_unibrasil}): {ceps[idx_unibrasil]}")
    print(f"   ✓ Coordenadas: {coords[idx_unibrasil]}")
    
    # Gera matriz de distâncias
    print(f"\n🗺️  GERANDO MATRIZ DE DISTÂNCIAS...")
    dist_matrix = generate_distance_matrix(coords)
    dist_total = sum(sum(row) for row in dist_matrix) / 2
    
    print(f"   ✓ Matriz {len(dist_matrix)}×{len(dist_matrix)} calculada")
    print(f"   ✓ Distância total possível: {dist_total:.2f} km")
    
    # Carrega ventos (opcional)
    wind_schedule = None
    if arquivo_ventos and arquivo_ventos.exists():
        try:
            import json
            print(f"\n🌬️  CARREGANDO PREVISÃO DE VENTOS...")
            print(f"   Arquivo: {arquivo_ventos}")
            
            with open(arquivo_ventos, 'r', encoding='utf-8') as f:
                wind_schedule = json.load(f)
            
            print(f"   ✓ Previsão de 7 dias carregada")
            
            # Resumo dos ventos
            print(f"\n   📋 Resumo dos Ventos:")
            for dia in sorted([int(d) for d in wind_schedule.keys()]):
                dia_str = str(dia)
                velocidades = [wind_schedule[dia_str][h]['velocidade_kmh'] 
                              for h in wind_schedule[dia_str].keys()]
                vel_min = min(velocidades)
                vel_max = max(velocidades)
                vel_med = sum(velocidades) / len(velocidades)
                print(f"      Dia {dia}: {vel_min:.0f}-{vel_max:.0f} km/h "
                      f"(média: {vel_med:.1f} km/h)")
        
        except Exception as e:
            print(f"\n⚠️  Erro ao carregar ventos: {e}")
            print(f"   Executando SEM considerar ventos")
            wind_schedule = None
    
    # Constrói cache de ventos
    wind_cache = build_wind_cache(wind_schedule)
    
    return ceps, coords, dist_matrix, idx_unibrasil, wind_cache, wind_schedule


def executar_algoritmo_genetico(ceps, coords, dist_matrix, idx_unibrasil, 
                                wind_cache, pop_size, generations):
    """
    Executa o algoritmo genético
    
    Returns:
        Tuple com (melhor_cromossomo, melhor_fitness, historico)
    """
    print(f"\n{'='*100}")
    print(" EXECUTANDO ALGORITMO GENÉTICO ".center(100))
    print(f"{'='*100}")
    
    melhor, melhor_fit, historico = evolve_optimized(
        ceps=ceps,
        coords=coords,
        dist_matrix=dist_matrix,
        idx_base=idx_unibrasil,
        wind_cache=wind_cache,
        pop_size=pop_size,
        generations=generations,
        verbose=True
    )
    
    return melhor, melhor_fit, historico


def analisar_resultado(melhor_fit, csv_rows, metricas, ceps):
    """Analisa e imprime resultado final"""
    print(f"\n{'='*100}")
    print(" RESULTADO FINAL ".center(100))
    print(f"{'='*100}")
    
    print(f"\n🏆 MELHOR SOLUÇÃO ENCONTRADA:")
    print(f"   • Fitness Total: {melhor_fit:,.0f}")
    print(f"   • Distância Total: {metricas['distancia_total_km']:.2f} km")
    print(f"   • Tempo Total: {str(timedelta(seconds=int(metricas['tempo_total_seg'])))}")
    print(f"   • Número de Pousos: {metricas['pousos']}")
    print(f"   • Pousos Tardios (após 17h): {metricas['pousos_tardios']}")
    print(f"   • Custo de Pousos: R$ {metricas['custo_reais']:.2f}")
    print(f"   • Dias Utilizados: {metricas['dias_usados']} / 7")
    
    # Decomposição do fitness
    custo_dist = metricas['distancia_total_km'] * Config.MULT_DISTANCIA
    custo_pousos = metricas['pousos'] * Config.MULT_POUSOS
    custo_tempo = metricas['tempo_total_seg'] * Config.MULT_TEMPO
    
    print(f"\n📊 DECOMPOSIÇÃO DO FITNESS:")
    print(f"   • DISTÂNCIA: {custo_dist:>15,.0f} pts ({custo_dist/melhor_fit*100:>5.1f}%)")
    print(f"   • POUSOS:    {custo_pousos:>15,.0f} pts ({custo_pousos/melhor_fit*100:>5.1f}%)")
    print(f"   • TEMPO:     {custo_tempo:>15,.0f} pts ({custo_tempo/melhor_fit*100:>5.1f}%)")
    
    # Validação
    validacao = validate_solution(csv_rows, ceps)
    
    print("\n✅ VALIDAÇÃO DOS REQUISITOS:")
    status_items = [
        ("Rota Fechada (Início/Fim Unibrasil)", 
         validacao['inicio_correto'] and validacao['fim_correto']),
        ("Todos os CEPs Visitados", validacao['todos_ceps']),
        ("Dentro do Prazo (7 dias)", validacao['dentro_prazo']),
        ("Velocidades Válidas (36-96, múltiplo 4)", validacao['velocidades_validas']),
        ("Horários Válidos (6h-19h)", validacao['horarios_validos'])
    ]
    
    all_valid = True
    for descricao, valido in status_items:
        status = "✔ OK" if valido else "✗ FALHA"
        print(f"   • {descricao}: {status}")
        if not valido:
            all_valid = False
    
    if not all_valid:
        print("\n⚠️  ATENÇÃO: SOLUÇÃO COM PROBLEMAS DE VALIDAÇÃO!")
        print("   Verifique os detalhes acima antes de entregar.")
    else:
        print("\n✓ Solução válida e pronta para entrega!")
    
    return all_valid


def salvar_resultados(csv_rows, arquivo_saida: str):
    """
    Salva resultados em arquivo CSV
    
    Args:
        csv_rows: Lista de dicionários com os dados
        arquivo_saida: Nome do arquivo de saída
    
    Returns:
        Path: Caminho completo do arquivo salvo
    """
    import csv
    
    output_path = OUTPUT_DIR / arquivo_saida
    
    fieldnames = list(csv_rows[0].keys())
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    return output_path


def gerar_visualizacoes(csv_rows, ceps, coords, idx_unibrasil, metricas, 
                       wind_schedule_path: Path = None):
    """Gera todos os gráficos de visualização"""
    print(f"\n📊 GERANDO VISUALIZAÇÕES...")
    
    try:
        # Define caminhos de saída no diretório output/
        graficos = {
            'ventos': OUTPUT_DIR / 'distribuicao_ventos.png',
            'mapa': OUTPUT_DIR / 'mapa_rota.png',
            'stats': OUTPUT_DIR / 'estatisticas_rota.png'
        }
        
        # 1. Gráfico de ventos
        if wind_schedule_path and wind_schedule_path.exists():
            import json
            with open(wind_schedule_path, 'r', encoding='utf-8') as f:
                wind_schedule = json.load(f)
            plotar_distribuicao_ventos(wind_schedule, str(graficos['ventos']))
        
        # 2. Mapa da rota
        plotar_mapa_rota(csv_rows, ceps, coords, idx_unibrasil, str(graficos['mapa']))
        
        # 3. Estatísticas
        plotar_estatisticas_rota(csv_rows, metricas, str(graficos['stats']))
        
        print("\n   ✓ Todos os gráficos gerados com sucesso!")
        
        return list(graficos.values())
    
    except Exception as e:
        print(f"\n   ⚠️  Erro ao gerar visualizações: {e}")
        import traceback
        traceback.print_exc()
        return []


def analisar_convergencia(historico):
    """Analisa e imprime estatísticas de convergência"""
    if len(historico['media']) <= 20:
        return
    
    print(f"\n{'='*100}")
    print(" ANÁLISE DE CONVERGÊNCIA ".center(100))
    print(f"{'='*100}")
    
    media_inicial = historico['media'][0]
    media_20 = historico['media'][20]
    media_final = historico['media'][-1]
    
    melhoria_ate_20 = ((media_inicial - media_20) / media_inicial) * 100
    melhoria_total = ((media_inicial - media_final) / media_inicial) * 100
    
    print(f"\n📈 Evolução da Média do Fitness:")
    print(f"   • Geração 0:            {media_inicial:>15,.0f}")
    print(f"   • Geração 20:           {media_20:>15,.0f}")
    print(f"   • Geração final:        {media_final:>15,.0f}")
    print(f"\n   • Melhoria (0→20):      {melhoria_ate_20:>14.2f}%")
    print(f"   • Melhoria total:       {melhoria_total:>14.2f}%")
    
    # Diagnóstico
    if melhoria_ate_20 >= 10:
        print(f"\n   ✓ CONVERGÊNCIA EXCELENTE (>10% em 20 gerações)")
        print(f"     Algoritmo está funcionando corretamente!")
    elif melhoria_ate_20 >= 5:
        print(f"\n   ⚠  CONVERGÊNCIA RAZOÁVEL (5-10% em 20 gerações)")
        print(f"     Considere aumentar população ou ajustar parâmetros.")
    else:
        print(f"\n   ✗ CONVERGÊNCIA FRACA (<5% em 20 gerações)")
        print(f"     ATENÇÃO: Revisar fitness ou parâmetros do AG!")


def imprimir_resumo_final(arquivo_csv: Path, graficos_gerados: list):
    """Imprime resumo final da execução"""
    print(f"\n{'='*100}")
    print(" EXECUÇÃO CONCLUÍDA COM SUCESSO ".center(100))
    print(f"{'='*100}")
    
    print(f"\n📁 ARQUIVOS GERADOS EM {OUTPUT_DIR}/:")
    print(f"\n   📄 DADOS:")
    print(f"      • {arquivo_csv.name}")
    
    if graficos_gerados:
        print(f"\n   📊 VISUALIZAÇÕES:")
        for grafico in graficos_gerados:
            if isinstance(grafico, Path):
                print(f"      • {grafico.name}")
    
    print(f"\n{'='*100}\n")


def main():
    """Função principal"""
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description="UNIBRASIL Surveyor - Otimização de Rota de Drone com AG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s coordenadas.csv
  %(prog)s coordenadas.csv --gen 200 --pop 150
  %(prog)s coordenadas.csv --wind ventos.json --seed 42
  %(prog)s coordenadas.csv --gen 300 --pop 200 --wind ventos.json --out rota_final.csv

Os arquivos de entrada devem estar em ./data/
Os arquivos de saída serão salvos em ./output/
        """
    )
    
    parser.add_argument(
        "arquivo",
        help="Nome do arquivo CSV com CEPs (deve estar em ./data/)"
    )
    parser.add_argument(
        "--wind",
        default="ventos.json",
        help="Nome do arquivo JSON com ventos (default: ventos.json)"
    )
    parser.add_argument(
        "--pop",
        type=int,
        default=Config.POP_SIZE,
        help=f"Tamanho da população (default: {Config.POP_SIZE})"
    )
    parser.add_argument(
        "--gen",
        type=int,
        default=200,
        help="Número de gerações (default: 200)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed para reprodutibilidade (default: aleatória)"
    )
    parser.add_argument(
        "--out",
        default="rota_saida.csv",
        help="Nome do arquivo CSV de saída (default: rota_saida.csv)"
    )
    
    args = parser.parse_args()
    
    # Configura seed se fornecida
    if args.seed:
        random.seed(args.seed)
        np.random.seed(args.seed)
    
    try:
        # Valida arquivos de entrada
        path_ceps, path_ventos = validar_arquivos_entrada(args.arquivo, args.wind)
        
        # Imprime cabeçalho e configuração
        imprimir_cabecalho()
        imprimir_configuracao(args, path_ventos is not None)
        
        # Valida escala do fitness
        print(f"\n{'='*100}")
        print(" VALIDAÇÃO DA ESCALA DO FITNESS ".center(100))
        print(f"{'='*100}")
        
        if not Config.validar_escala():
            resposta = input("\n⚠️  Escala pode causar problemas. Continuar? (s/n): ")
            if resposta.lower() != 's':
                print("Execução abortada pelo usuário.")
                return 1
        
        # Carrega dados
        ceps, coords, dist_matrix, idx_unibrasil, wind_cache, wind_schedule = \
            carregar_dados(path_ceps, path_ventos)
        
        # Executa AG
        melhor, melhor_fit, historico = executar_algoritmo_genetico(
            ceps, coords, dist_matrix, idx_unibrasil, wind_cache,
            args.pop, args.gen
        )
        
        # Simula rota detalhada
        csv_rows, metricas = simulate_route_detailed(
            melhor, ceps, coords, dist_matrix, wind_cache
        )
        
        # Analisa resultado
        valido = analisar_resultado(melhor_fit, csv_rows, metricas, ceps)
        
        # Salva CSV
        arquivo_salvo = salvar_resultados(csv_rows, args.out)
        print(f"\n💾 Rota salva em: {arquivo_salvo}")
        
        # Gera visualizações
        graficos = gerar_visualizacoes(
            csv_rows, ceps, coords, idx_unibrasil, metricas, path_ventos
        )
        
        # Analisa convergência
        analisar_convergencia(historico)
        
        # Resumo final
        imprimir_resumo_final(arquivo_salvo, graficos)
        
        return 0 if valido else 1
    
    except FileNotFoundError as e:
        print(f"\n❌ ERRO: {e}", file=sys.stderr)
        return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário.")
        return 130
    
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())