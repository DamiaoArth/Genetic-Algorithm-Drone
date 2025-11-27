# data_loader.py
import csv
import math
from typing import List, Tuple, Dict, Optional
from config import Config

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância entre dois pontos usando a fórmula de Haversine.
    
    Conforme especificado no PDF (página com exemplo do ChatGPT).
    
    Args:
        lat1, lon1: Latitude e longitude do ponto 1 (em graus)
        lat2, lon2: Latitude e longitude do ponto 2 (em graus)
    
    Returns:
        Distância em quilômetros
    """
    # Raio da Terra em km
    R = 6371.0
    
    # Converte graus para radianos
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferenças
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distancia = R * c
    
    return distancia

def load_ceps_coords(filepath: str) -> Tuple[List[str], List[Tuple[float, float]], int]:
    """
    Carrega CEPs e coordenadas do arquivo CSV.
    
    Formato esperado do CSV:
    cep,latitude,longitude
    82821020,-25.4524871,-49.2925963
    ...
    
    Args:
        filepath: Caminho do arquivo CSV
    
    Returns:
        (lista_ceps, lista_coordenadas, indice_unibrasil)
        
    Raises:
        FileNotFoundError: Se arquivo não existir
        ValueError: Se CEP da Unibrasil não for encontrado
    """
    ceps = []
    coords = []
    idx_unibrasil = None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Verifica se as colunas necessárias existem
            if not all(col in reader.fieldnames for col in ['cep', 'latitude', 'longitude']):
                raise ValueError(f"CSV deve conter colunas: cep, latitude, longitude. "
                               f"Encontrado: {reader.fieldnames}")
            
            for idx, row in enumerate(reader):
                try:
                    cep = row['cep'].strip()
                    lat = float(row['latitude'])
                    lon = float(row['longitude'])
                    
                    ceps.append(cep)
                    coords.append((lat, lon))
                    
                    # Identifica índice da Unibrasil
                    if cep == Config.CEP_UNIBRASIL:
                        idx_unibrasil = idx
                        
                except (ValueError, KeyError) as e:
                    raise ValueError(f"Erro ao processar linha {idx+2}: {row}. Erro: {e}")
        
        if not ceps:
            raise ValueError("Arquivo CSV está vazio ou não contém dados válidos")
        
        if idx_unibrasil is None:
            raise ValueError(f"CEP da Unibrasil ({Config.CEP_UNIBRASIL}) não encontrado no arquivo!")
        
        return ceps, coords, idx_unibrasil
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    except Exception as e:
        raise Exception(f"Erro ao carregar arquivo {filepath}: {e}")

def generate_distance_matrix(coords: List[Tuple[float, float]]) -> List[List[float]]:
    """
    Gera matriz de distâncias entre todos os pontos usando Haversine.
    
    Args:
        coords: Lista de tuplas (latitude, longitude)
    
    Returns:
        Matriz NxN onde matrix[i][j] = distância entre ponto i e j em km
    """
    n = len(coords)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = haversine(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
            matrix[i][j] = dist
            matrix[j][i] = dist  # Matriz simétrica
    
    return matrix

def build_wind_cache(wind_schedule: Optional[Dict] = None) -> Dict[Tuple[int, int], Tuple[float, float]]:
    """
    Constrói cache de vento para acesso rápido durante a simulação.
    
    Estrutura do wind_schedule (JSON):
    {
        "1": {  // Dia 1
            "6": {"velocidade_kmh": 9.0, "direcao_graus": 157.5},
            "9": {"velocidade_kmh": 11.0, "direcao_graus": 180.0},
            ...
        },
        "2": { ... },
        ...
    }
    
    Args:
        wind_schedule: Dicionário com previsão de ventos (opcional)
    
    Returns:
        Dicionário {(dia, hora): (velocidade_kmh, direcao_graus)}
        
    Exemplo:
        cache[(1, 6)] = (9.0, 157.5)  # Dia 1, 6h: 9 km/h de SSE
    """
    cache = {}
    
    if wind_schedule is None:
        # Sem vento (simplificação para testes)
        for dia in range(1, 8):  # 7 dias
            for hora in [6, 9, 12, 15, 18]:
                cache[(dia, hora)] = (0.0, 0.0)
        return cache
    
    try:
        for dia_str, horarios in wind_schedule.items():
            dia = int(dia_str)
            
            for hora_str, dados in horarios.items():
                hora = int(hora_str)
                
                velocidade = float(dados.get('velocidade_kmh', 0.0))
                direcao = float(dados.get('direcao_graus', 0.0))
                
                cache[(dia, hora)] = (velocidade, direcao)
    
    except (ValueError, KeyError, TypeError) as e:
        print(f"⚠️  Aviso: Erro ao processar previsão de ventos: {e}")
        print(f"   Usando vento zero para todas as horas.")
        
        # Fallback: sem vento
        for dia in range(1, 8):
            for hora in [6, 9, 12, 15, 18]:
                cache[(dia, hora)] = (0.0, 0.0)
    
    return cache

def validar_arquivo_csv(filepath: str) -> Dict[str, any]:
    """
    Valida o arquivo CSV antes de processar.
    
    Args:
        filepath: Caminho do arquivo
    
    Returns:
        Dicionário com informações da validação:
        {
            'valido': bool,
            'num_linhas': int,
            'tem_unibrasil': bool,
            'erros': List[str]
        }
    """
    resultado = {
        'valido': True,
        'num_linhas': 0,
        'tem_unibrasil': False,
        'erros': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Valida cabeçalho
            colunas_necessarias = ['cep', 'latitude', 'longitude']
            colunas_faltando = [col for col in colunas_necessarias if col not in reader.fieldnames]
            
            if colunas_faltando:
                resultado['valido'] = False
                resultado['erros'].append(f"Colunas faltando: {', '.join(colunas_faltando)}")
                return resultado
            
            # Valida linhas
            for idx, row in enumerate(reader):
                resultado['num_linhas'] += 1
                
                # Valida CEP
                cep = row['cep'].strip()
                if not cep or not cep.isdigit() or len(cep) != 8:
                    resultado['erros'].append(f"Linha {idx+2}: CEP inválido '{cep}'")
                
                if cep == Config.CEP_UNIBRASIL:
                    resultado['tem_unibrasil'] = True
                
                # Valida coordenadas
                try:
                    lat = float(row['latitude'])
                    lon = float(row['longitude'])
                    
                    # Valida range (Curitiba aproximadamente)
                    if not (-26.0 <= lat <= -25.0):
                        resultado['erros'].append(f"Linha {idx+2}: Latitude fora do range esperado: {lat}")
                    
                    if not (-49.5 <= lon <= -49.0):
                        resultado['erros'].append(f"Linha {idx+2}: Longitude fora do range esperado: {lon}")
                        
                except ValueError:
                    resultado['erros'].append(f"Linha {idx+2}: Coordenadas inválidas")
            
            if resultado['num_linhas'] == 0:
                resultado['valido'] = False
                resultado['erros'].append("Arquivo vazio (sem dados)")
            
            if not resultado['tem_unibrasil']:
                resultado['valido'] = False
                resultado['erros'].append(f"CEP da Unibrasil ({Config.CEP_UNIBRASIL}) não encontrado")
            
            if len(resultado['erros']) > 0:
                resultado['valido'] = False
    
    except FileNotFoundError:
        resultado['valido'] = False
        resultado['erros'].append(f"Arquivo não encontrado: {filepath}")
    except Exception as e:
        resultado['valido'] = False
        resultado['erros'].append(f"Erro ao ler arquivo: {e}")
    
    return resultado

# ===========================
# FUNÇÕES AUXILIARES
# ===========================

def calcular_estatisticas_distancias(dist_matrix: List[List[float]]) -> Dict[str, float]:
    """
    Calcula estatísticas da matriz de distâncias.
    
    Args:
        dist_matrix: Matriz de distâncias NxN
    
    Returns:
        Dicionário com estatísticas:
        {
            'min': distância mínima (exceto 0),
            'max': distância máxima,
            'media': distância média,
            'total': soma de todas as distâncias (excluindo diagonal)
        }
    """
    n = len(dist_matrix)
    distancias = []
    
    for i in range(n):
        for j in range(i + 1, n):
            distancias.append(dist_matrix[i][j])
    
    return {
        'min': min(distancias),
        'max': max(distancias),
        'media': sum(distancias) / len(distancias),
        'total': sum(distancias)
    }

def encontrar_k_vizinhos_mais_proximos(idx: int, dist_matrix: List[List[float]], k: int = 5) -> List[Tuple[int, float]]:
    """
    Encontra os k vizinhos mais próximos de um ponto.
    
    Args:
        idx: Índice do ponto
        dist_matrix: Matriz de distâncias
        k: Número de vizinhos
    
    Returns:
        Lista de tuplas (índice_vizinho, distância) ordenada por distância
    """
    n = len(dist_matrix)
    distancias = [(j, dist_matrix[idx][j]) for j in range(n) if j != idx]
    distancias.sort(key=lambda x: x[1])
    
    return distancias[:k]

# ===========================
# TESTE DO MÓDULO
# ===========================
if __name__ == "__main__":
    print("="*70)
    print(" TESTE DO DATA_LOADER")
    print("="*70)
    
    # Teste 1: Validação de arquivo
    print("\nTeste 1: Validação de arquivo CSV")
    print("-" * 70)
    
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "ceps_coords.csv"
    
    validacao = validar_arquivo_csv(filepath)
    
    if validacao['valido']:
        print(f"✓ Arquivo válido!")
        print(f"  Linhas: {validacao['num_linhas']}")
        print(f"  Unibrasil encontrada: {validacao['tem_unibrasil']}")
    else:
        print(f"✗ Arquivo inválido!")
        for erro in validacao['erros']:
            print(f"  - {erro}")
        sys.exit(1)
    
    # Teste 2: Carregamento de dados
    print("\n\nTeste 2: Carregamento de dados")
    print("-" * 70)
    
    try:
        ceps, coords, idx_unibrasil = load_ceps_coords(filepath)
        print(f"✓ {len(ceps)} CEPs carregados")
        print(f"✓ Unibrasil no índice {idx_unibrasil}: {ceps[idx_unibrasil]}")
        print(f"  Coordenadas: {coords[idx_unibrasil]}")
    except Exception as e:
        print(f"✗ Erro ao carregar: {e}")
        sys.exit(1)
    
    # Teste 3: Matriz de distâncias
    print("\n\nTeste 3: Geração de matriz de distâncias")
    print("-" * 70)
    
    dist_matrix = generate_distance_matrix(coords)
    print(f"✓ Matriz {len(dist_matrix)}×{len(dist_matrix)} gerada")
    
    stats = calcular_estatisticas_distancias(dist_matrix)
    print(f"\nEstatísticas:")
    print(f"  Distância mínima: {stats['min']:.2f} km")
    print(f"  Distância máxima: {stats['max']:.2f} km")
    print(f"  Distância média:  {stats['media']:.2f} km")
    print(f"  Distância total:  {stats['total']:.2f} km")
    
    # Teste 4: Vizinhos mais próximos da Unibrasil
    print("\n\nTeste 4: 5 vizinhos mais próximos da Unibrasil")
    print("-" * 70)
    
    vizinhos = encontrar_k_vizinhos_mais_proximos(idx_unibrasil, dist_matrix, k=5)
    
    for idx, (viz_idx, dist) in enumerate(vizinhos, 1):
        print(f"{idx}. CEP {ceps[viz_idx]}: {dist:.2f} km")
    
    # Teste 5: Cache de vento (sem vento)
    print("\n\nTeste 5: Cache de vento (padrão: sem vento)")
    print("-" * 70)
    
    wind_cache = build_wind_cache(None)
    print(f"✓ Cache criado com {len(wind_cache)} entradas")
    print(f"  Exemplo - Dia 1, 6h: {wind_cache[(1, 6)]}")
    print(f"  Exemplo - Dia 3, 12h: {wind_cache[(3, 12)]}")
    
    print("\n" + "="*70)
    print(" TODOS OS TESTES CONCLUÍDOS COM SUCESSO")
    print("="*70)
