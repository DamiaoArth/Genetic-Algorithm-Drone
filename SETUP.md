# 🚀 Guia de Configuração Rápida - UNIBRASIL Surveyor

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes)
- Git (opcional)

---

## 🔧 Instalação Passo a Passo

### **1. Criar Ambiente Virtual**

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### **2. Instalar Dependências**

```bash
pip install -r requirements.txt
```

Isso instalará:
- `numpy` - Computação numérica
- `matplotlib` - Visualizações
- `pytest` (opcional) - Testes

### **3. Verificar Instalação**

```bash
python -c "import numpy, matplotlib; print('✓ Dependências OK!')"
```

---

## 📁 Preparar Dados de Entrada

### **Arquivo Obrigatório: `data/coordenadas.csv`**

Formato:
```csv
cep,latitude,longitude
82821020,-25.4524871,-49.2925963
80050370,-25.4376831,-49.2729254
...
```

**⚠️ IMPORTANTE:**
- CEP da Unibrasil (`82821020`) **DEVE** estar presente
- Sem espaços extras
- Vírgula como separador

### **Arquivo Opcional: `data/ventos.json`**

Formato:
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

## ▶️ Executar o Sistema

### **Teste Rápido (10 gerações):**
```bash
python main.py coordenadas.csv --gen 10 --pop 20
```

### **Execução Padrão (200 gerações, sem ventos):**
```bash
python main.py coordenadas.csv
```

### **Execução Completa (COM ventos):**
```bash
python main.py coordenadas.csv --wind ventos.json --gen 200 --pop 150
```

### **Execução Longa (melhor resultado):**
```bash
python main.py coordenadas.csv --wind ventos.json --gen 500 --pop 300 --seed 42
```

---

## 📊 Verificar Resultados

Após execução, você terá em `output/`:

```
output/
├── rota_saida.csv              ← ARQUIVO PARA ENTREGAR
├── distribuicao_ventos.png     ← Gráfico dos ventos
├── mapa_rota.png               ← Mapa da rota
└── estatisticas_rota.png       ← Estatísticas detalhadas
```

---

## ✅ Checklist de Validação

Execute ANTES de entregar:

```bash
# 1. Arquivos de dados presentes?
ls -la data/
# Deve mostrar: coordenadas.csv, ventos.json (opcional)

# 2. Ambiente virtual ativo?
which python
# Deve mostrar: .../venv/bin/python ou ...\venv\Scripts\python

# 3. Execução completa sem erros?
python main.py coordenadas.csv --wind ventos.json --gen 100 --pop 100

# 4. Arquivos de saída gerados?
ls -la output/
# Deve mostrar: 4 arquivos (.csv + 3 .png)

# 5. Validação passou?
# Veja no terminal:
# ✅ VALIDAÇÃO DOS REQUISITOS:
#    • Rota Fechada (Início/Fim Unibrasil): ✔ OK
#    • Todos os CEPs Visitados: ✔ OK
#    • Dentro do Prazo (7 dias): ✔ OK
#    • Velocidades Válidas (36-96, múltiplo 4): ✔ OK
#    • Horários Válidos (6h-19h): ✔ OK
```

---

## ⚠️ Problemas Comuns

### **"ModuleNotFoundError: No module named 'core'"**
**Causa:** Executando do diretório errado  
**Solução:**
```bash
cd unibrasil-surveyor/  # Ir para raiz do projeto
python main.py coordenadas.csv
```

### **"FileNotFoundError: coordenadas.csv"**
**Causa:** Arquivo não está em `data/`  
**Solução:**
```bash
ls data/  # Verificar conteúdo
# Se vazio, adicione o arquivo:
cp /seu/caminho/coordenadas.csv data/
```

### **Convergência fraca (<5% em 20 gerações)**
**Causa:** Parâmetros insuficientes  
**Solução:**
```bash
python main.py coordenadas.csv --gen 400 --pop 250
```

### **"ImportError: cannot import name 'gerar_todos_graficos'"**
**Causa:** `main.py` com import errado  
**Solução:** Use o `main.py` corrigido fornecido

---

## 📞 Suporte

**Autores:**
- Arthur Damiao Mendes (2023102413)
- Gabryel Zanella (2023100930)
- Luiz Felipe (2023201245)

**Disciplina:** Serviços Cognitivos  
**Professor:** Mozart Hasse  
**Instituição:** Unibrasil

---

## 🎯 Próximos Passos

1. ✅ Ambiente configurado
2. ✅ Dependências instaladas
3. ⚠️ **VOCÊ ESTÁ AQUI** - Adicionar arquivos de dados
4. ⬜ Executar testes
5. ⬜ Executar sistema completo
6. ⬜ Validar resultados
7. ⬜ Entregar `rota_saida.csv`

**Versão:** 3.0.2  
**Data:** 2025  
**Status:** ✅ Pronto para uso