# 🚁 UNIBRASIL Surveyor

Sistema de otimização de rotas para drone autônomo usando Algoritmo Genético.

## 📋 Descrição do Projeto

O UNIBRASIL Surveyor é um sistema desenvolvido para planejar rotas otimizadas de um drone autônomo que deve fotografar diversos CEPs na cidade de Curitiba. O objetivo é **minimizar o custo total**, medido pelo tempo de voo e quantidade de paradas para recarga.

**Disciplina:** Serviços Cognitivos  
**Professor:** Mozart Hasse  
**Instituição:** Unibrasil

---

## 🎯 Objetivos do Sistema

1. **Minimizar tempo total de voo**
2. **Minimizar número de recargas**
3. **Respeitar todas as restrições operacionais**:
   - Autonomia da bateria
   - Janela de operação (6h-19h)
   - Prazo de 7 dias
   - Efeito dos ventos
   - Velocidades válidas

---

## 📁 Estrutura do Projeto

```
unibrasil-surveyor/
├── main.py                     # Script principal de execução
├── requirements.txt            # Dependências Python
├── README.md                   # Esta documentação
├── .gitignore                  # Arquivos ignorados pelo Git
│
├── data/                       # Arquivos de entrada
│   ├── coordenadas.csv         # CEPs e coordenadas (fornecido pelo professor)
│   └── ventos.json             # Previsão de ventos (7 dias)
│
├── core/                       # Código fonte principal
│   ├── __init__.py
│   ├── config.py               # Configurações e parâmetros
│   ├── data_loader.py          # Carregamento de dados
│   ├── physics.py              # Física do drone (aceleração, vento)
│   ├── simulation.py           # Simulação de rotas e fitness
│   ├── genetic_algorithm.py    # Algoritmo Genético
│   └── visualizacao.py         # Geração de gráficos
│
├── output/                     # Arquivos gerados
│   ├── rota_saida.csv          # Solução encontrada
│   ├── distribuicao_ventos.png # Gráfico dos ventos
│   ├── mapa_rota.png           # Mapa da rota
│   ├── estatisticas_rota.png   # Estatísticas
│   └── monitoramento_*.png     # Evolução do AG
│
└── tests/                      # Testes unitários
    ├── __init__.py
    ├── test_data_loader.py
    ├── test_simulation.py
    └── test_genetic_algorithm.py
```

---

## 🚀 Instalação e Execução

### **Pré-requisitos**

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### **1. Clonar/Extrair o Projeto**

```bash
# Se estiver em um repositório Git:
git clone <url-do-repositorio>
cd unibrasil-surveyor

# Ou extrair o ZIP fornecido
unzip unibrasil-surveyor.zip
cd unibrasil-surveyor
```

### **2. Instalar Dependências**

```bash
pip install -r requirements.txt
```

### **3. Preparar Dados de Entrada**

Certifique-se de que os arquivos estão no diretório `data/`:

```
data/
├── coordenadas.csv    # CEPs e coordenadas (obrigatório)
└── ventos.json        # Previsão de ventos (opcional)
```

### **4. Executar o Sistema**

**Execução básica (sem ventos):**
```bash
python main.py coordenadas.csv
```

**Execução completa (com ventos):**
```bash
python main.py coordenadas.csv --wind ventos.json
```

**Execução com parâmetros customizados:**
```bash
python main.py coordenadas.csv \
    --wind ventos.json \
    --gen 300 \
    --pop 200 \
    --seed 42 \
    --out rota_final.csv
```

### **5. Parâmetros Disponíveis**

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `arquivo` | Arquivo CSV com CEPs (obrigatório) | - |
| `--wind` | Arquivo JSON com ventos | `ventos.json` |
| `--pop` | Tamanho da população | `150` |
| `--gen` | Número de gerações | `200` |
| `--seed` | Seed para reprodutibilidade | Aleatória |
| `--out` | Nome do arquivo de saída | `rota_saida.csv` |

**Exemplos:**

```bash
# Teste rápido (10 gerações, população pequena)
python main.py coordenadas.csv --gen 10 --pop 20

# Execução com seed fixa (reproduzível)
python main.py coordenadas.csv --seed 42

# Execução longa para melhor resultado
python main.py coordenadas.csv --gen 500 --pop 300
```

---

## 📊 Saídas Geradas

Todos os arquivos são salvos no diretório `output/`:

### **1. rota_saida.csv**
Arquivo CSV com a rota detalhada. Formato:

```csv
cep_inicial,lat_inicial,lon_inicial,dia,hora_inicial,velocidade,cep_final,lat_final,lon_final,pouso,hora_final
82821020,-25.4524871,-49.2925963,1,06:00:00,72,80050370,-25.4376831,-49.2729254,NÃO,06:12:34
...
```

### **2. Gráficos de Visualização**

- **distribuicao_ventos.png**: Velocidade e direção dos ventos por dia
- **mapa_rota.png**: Mapa da rota (latitude × longitude)
- **estatisticas_rota.png**: Estatísticas detalhadas (pousos, velocidades, etc.)
- **monitoramento_completo.png**: Evolução do fitness ao longo das gerações

---

## ⚙️ Configuração do Sistema

### **Parâmetros do Drone (config.py)**

```python
VELOCIDADE_MAXIMA = 96        # km/h
VELOCIDADE_MINIMA = 36        # km/h (10 m/s)
AUTONOMIA_BASE_SEG = 4650.0   # ~77.5 minutos (fator Curitiba: 0.93)
TEMPO_PARADA_SEG = 72         # 1min 12s por parada
TEMPO_RECARGA_SEG = 3600      # 1 hora
```

### **Parâmetros do Algoritmo Genético**

```python
POP_SIZE = 150                # Tamanho da população
CROSSOVER_RATE = 0.85         # Taxa de crossover
MUTATION_RATE_SWAP = 0.12     # Taxa de mutação (swap)
MUTATION_RATE_INVERSION = 0.08  # Taxa de mutação (inversion)
MUTATION_RATE_2OPT = 0.05     # Taxa de mutação (2-opt)
ELITISM_COUNT = 5             # Número de elites preservadas
TOURNAMENT_SIZE = 3           # Tamanho do torneio
```

### **Função Fitness (Hierarquia Lexicográfica)**

```python
FITNESS = Distância × 1.000.000    # Fator dominante (~87%)
        + Pousos × 1.000           # Desempate médio (~1%)
        + Tempo × 1                # Desempate fino (~9%)
        + Penalidades              # Violações graves (~3%)
```

**Exemplo:**
- 100m de distância = 100.000 pontos
- 1 pouso = 1.000 pontos
- 1.000 segundos = 1.000 pontos

**Garantia:** 100m > 50 pousos + 200.000 segundos

---

## 🧬 Algoritmo Genético

### **Representação**

- **Cromossomo:** Permutação dos CEPs + vetor de velocidades
- **Rota:** [base, cep1, cep2, ..., cepN, base]
- **Velocidades:** [v1, v2, ..., vN+1] (em km/h, múltiplos de 4)

### **Operadores**

1. **Seleção:** Torneio (k=3)
2. **Crossover:** Order Crossover (OX) - preserva ordem
3. **Mutação:** 
   - Swap (troca 2 posições)
   - Inversion (inverte subsegmento)
   - 2-opt (remove cruzamentos)
4. **Elitismo:** Mantém 5 melhores indivíduos

### **Anti-Estagnação**

- Detecção a cada 20 gerações
- Restart parcial (30% novos indivíduos)
- Hiper-mutação (taxa 40%)
- Local search 2-opt nos melhores

---

## 🌬️ Consideração de Ventos

O sistema considera os efeitos do vento conforme especificação:

### **Efeito na Velocidade**

```
velocidade_efetiva = velocidade_drone + componente_vento

componente_vento = vento × cos(ângulo_relativo)
```

- **Vento a favor** (0°): aumenta velocidade
- **Vento contrário** (180°): reduz velocidade
- **Vento lateral** (90°): sem efeito direto

### **Formato do arquivo ventos.json**

```json
{
  "1": {
    "6": {"velocidade_kmh": 9.0, "direcao_graus": 157.5},
    "9": {"velocidade_kmh": 11.0, "direcao_graus": 180.0},
    "12": {"velocidade_kmh": 15.0, "direcao_graus": 202.5},
    "15": {"velocidade_kmh": 17.0, "direcao_graus": 225.0},
    "18": {"velocidade_kmh": 13.0, "direcao_graus": 202.5}
  },
  "2": { ... },
  ...
  "7": { ... }
}
```

---

## ✅ Validação da Solução

O sistema valida automaticamente:

1. ✓ Rota fechada (inicia e termina na Unibrasil)
2. ✓ Todos os CEPs visitados exatamente uma vez
3. ✓ Dentro do prazo (7 dias)
4. ✓ Velocidades válidas (36-96 km/h, múltiplos de 4)
5. ✓ Horários válidos (6h-19h)
6. ✓ Autonomia respeitada (pousos quando necessário)

**Output da validação:**
```
✅ VALIDAÇÃO DOS REQUISITOS:
   • Rota Fechada (Início/Fim Unibrasil): ✓ OK
   • Todos os CEPs Visitados: ✓ OK
   • Dentro do Prazo (7 dias): ✓ OK
   • Velocidades Válidas (36-96, múltiplo 4): ✓ OK
   • Horários Válidos (6h-19h): ✓ OK
```

---

## 🧪 Testes

### **Executar Testes Unitários**

```bash
# Instalar pytest
pip install pytest pytest-cov

# Executar todos os testes
pytest tests/

# Executar com cobertura
pytest --cov=core tests/

# Executar teste específico
pytest tests/test_simulation.py -v
```

### **Estrutura dos Testes**

```
tests/
├── test_data_loader.py      # Testa carregamento de dados
├── test_simulation.py       # Testa simulação e fitness
└── test_genetic_algorithm.py # Testa operadores do AG
```

---

## 📈 Interpretação dos Resultados

### **Fitness**

- **Fitness < 50.000.000** (para ~50 CEPs): Excelente
- **Fitness < 60.000.000**: Bom
- **Fitness > 70.000.000**: Revisar parâmetros

### **Convergência**

- **Melhoria > 10% em 20 gerações**: Excelente
- **Melhoria 5-10% em 20 gerações**: Razoável
- **Melhoria < 5% em 20 gerações**: Problema detectado

### **Métricas Típicas (50 CEPs)**

- Distância: 40-55 km
- Tempo: 20-30 horas
- Pousos: 5-12
- Dias: 2-4

---

## 🐛 Troubleshooting

### **Erro: "Arquivo não encontrado"**

**Solução:** Certifique-se de que os arquivos estão em `data/`:
```bash
ls -la data/
# Deve mostrar: coordenadas.csv e ventos.json
```

### **Erro: "No module named 'core'"**

**Solução:** Execute a partir do diretório raiz do projeto:
```bash
cd unibrasil-surveyor
python main.py coordenadas.csv
```

### **Convergência fraca (< 5% em 20 gerações)**

**Solução:** Ajustar parâmetros:
```bash
# Aumentar população e gerações
python main.py coordenadas.csv --gen 400 --pop 250

# Testar com seed diferente
python main.py coordenadas.csv --seed 123
```

### **Muitas soluções inviáveis**

**Causa:** Autonomia insuficiente para os dados  
**Solução:** Verificar se `AUTONOMIA_BASE_SEG` está correto (4650s)

---

## 🔬 Detalhes Técnicos

### **Física do Drone**

- **Aceleração:** 2.0 m/s²
- **Desaceleração:** 3.0 m/s²
- **Consumo:** Proporcional à velocidade^1.5
- **Velocidade de referência:** 36 km/h (mais eficiente)

### **Simulação em Duas Camadas**

1. **Rápida (fitness):** Estimativa sem física detalhada (10-20× mais rápido)
2. **Detalhada (CSV):** Física completa apenas na solução final

### **Escala Lexicográfica**

Garante que distância sempre domina:
```
100m de distância = 100.000 pontos
> 50 pousos (50.000 pontos) + 200.000s (200.000 pontos)
```

---

## 📚 Referências

1. **Algoritmos Genéticos:** Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning.
2. **TSP:** Laporte, G. (1992). The traveling salesman problem: An overview of exact and approximate algorithms.
3. **Haversine:** Vincenty, T. (1975). Direct and inverse solutions of geodesics on the ellipsoid.

---

## 👥 Autores

- Arthur Damiao Mendes (matricula: 2023102413)
- Gabryel Zanella (matricula: 2023100930)
- Luiz Felipe (matricula: 2023201245)

---

## 📄 Licença

Este projeto é parte de uma atividade acadêmica da disciplina de Serviços Cognitivos da Unibrasil.

---

## 📞 Suporte

Em caso de dúvidas ou problemas:

1. Verifique esta documentação completa
2. Consulte os comentários no código
3. Execute os testes unitários
4. Entre em contato com o professor

---

**Versão:** 3.0.2  
**Data:** 2025  
**Status:** ✅ Pronto para entrega