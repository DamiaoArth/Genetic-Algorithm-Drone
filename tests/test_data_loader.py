"""
Testes Unitários para data_loader.py

Testa funções de carregamento e processamento de dados.
"""

import pytest
import sys
from pathlib import Path

# Adiciona core ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from core.data_loader import (
    haversine,
    generate_distance_matrix,
    validar_arquivo_csv,
    calcular_estatisticas_distancias
)


class TestHaversine:
    """Testes para cálculo de distância Haversine"""
    
    def test_mesma_coordenada(self):
        """Distância entre mesmo ponto deve ser 0"""
        lat, lon = -25.4524871, -49.2925963
        dist = haversine(lat, lon, lat, lon)
        assert dist == 0.0, "Distância entre mesmo ponto deve ser 0"
    
    def test_distancia_conhecida(self):
        """Testa distância conhecida (aproximadamente)"""
        # Curitiba (Unibrasil) para outro ponto
        lat1, lon1 = -25.4524871, -49.2925963
        lat2, lon2 = -25.4376831, -49.2729254
        
        dist = haversine(lat1, lon1, lat2, lon2)
        
        # Distância deve ser aproximadamente 2-3 km
        assert 1.5 < dist < 3.5, f"Distância fora do esperado: {dist} km"
    
    def test_distancia_simetrica(self):
        """Distância deve ser simétrica (A→B = B→A)"""
        lat1, lon1 = -25.4524871, -49.2925963
        lat2, lon2 = -25.4376831, -49.2729254
        
        dist_ab = haversine(lat1, lon1, lat2, lon2)
        dist_ba = haversine(lat2, lon2, lat1, lon1)
        
        assert abs(dist_ab - dist_ba) < 0.001, "Distância deve ser simétrica"


class TestDistanceMatrix:
    """Testes para geração de matriz de distâncias"""
    
    def test_matriz_quadrada(self):
        """Matriz deve ser quadrada (NxN)"""
        coords = [
            (-25.4524871, -49.2925963),
            (-25.4376831, -49.2729254),
            (-25.4450000, -49.2800000)
        ]
        
        matrix = generate_distance_matrix(coords)
        
        assert len(matrix) == len(coords), "Matriz deve ter N linhas"
        for row in matrix:
            assert len(row) == len(coords), "Matriz deve ter N colunas"
    
    def test_diagonal_zeros(self):
        """Diagonal principal deve ser zero"""
        coords = [
            (-25.4524871, -49.2925963),
            (-25.4376831, -49.2729254),
        ]
        
        matrix = generate_distance_matrix(coords)
        
        for i in range(len(coords)):
            assert matrix[i][i] == 0.0, f"Diagonal[{i}][{i}] deve ser 0"
    
    def test_matriz_simetrica(self):
        """Matriz deve ser simétrica (matrix[i][j] = matrix[j][i])"""
        coords = [
            (-25.4524871, -49.2925963),
            (-25.4376831, -49.2729254),
            (-25.4450000, -49.2800000)
        ]
        
        matrix = generate_distance_matrix(coords)
        
        n = len(coords)
        for i in range(n):
            for j in range(n):
                diff = abs(matrix[i][j] - matrix[j][i])
                assert diff < 0.001, f"Matriz não simétrica em [{i}][{j}]"


class TestValidacaoCSV:
    """Testes para validação de arquivos CSV"""
    
    def test_validacao_arquivo_inexistente(self):
        """Arquivo inexistente deve falhar"""
        resultado = validar_arquivo_csv("arquivo_que_nao_existe.csv")
        
        assert resultado['valido'] == False, "Arquivo inexistente deve ser inválido"
        assert len(resultado['erros']) > 0, "Deve haver mensagem de erro"
    
    def test_validacao_estrutura(self):
        """Testa estrutura do resultado de validação"""
        resultado = validar_arquivo_csv("qualquer.csv")
        
        # Verifica se todas as chaves esperadas existem
        assert 'valido' in resultado
        assert 'num_linhas' in resultado
        assert 'tem_unibrasil' in resultado
        assert 'erros' in resultado


class TestEstatisticas:
    """Testes para cálculo de estatísticas"""
    
    def test_estatisticas_matriz_pequena(self):
        """Testa estatísticas de matriz pequena"""
        # Matriz 3x3 simples
        matrix = [
            [0.0, 2.0, 4.0],
            [2.0, 0.0, 3.0],
            [4.0, 3.0, 0.0]
        ]
        
        stats = calcular_estatisticas_distancias(matrix)
        
        assert stats['min'] == 2.0, "Mínimo deve ser 2.0"
        assert stats['max'] == 4.0, "Máximo deve ser 4.0"
        assert 'media' in stats
        assert 'total' in stats


# ===========================
# TESTES DE INTEGRAÇÃO
# ===========================

class TestIntegracao:
    """Testes de integração entre componentes"""
    
    def test_fluxo_completo_pequeno(self):
        """Testa fluxo completo com dados pequenos"""
        # Dados de teste
        coords = [
            (-25.4524871, -49.2925963),  # Unibrasil
            (-25.4376831, -49.2729254),
            (-25.4450000, -49.2800000)
        ]
        
        # Gera matriz
        matrix = generate_distance_matrix(coords)
        
        # Verifica dimensões
        assert len(matrix) == 3
        assert len(matrix[0]) == 3
        
        # Calcula estatísticas
        stats = calcular_estatisticas_distancias(matrix)
        
        # Verifica que as estatísticas fazem sentido
        assert stats['min'] > 0, "Distância mínima deve ser positiva"
        assert stats['max'] > stats['min'], "Máximo deve ser maior que mínimo"
        assert stats['media'] > 0, "Média deve ser positiva"


# ===========================
# CONFIGURAÇÃO DO PYTEST
# ===========================

if __name__ == "__main__":
    # Permite executar testes diretamente
    pytest.main([__file__, "-v"])