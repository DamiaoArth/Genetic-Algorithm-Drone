# Quick Setup Guide – UNIBRASIL Surveyor

## Prerequisites

* Python 3.8 or higher
* pip (package manager)
* Git (optional)

---

## Step-by-Step Installation

### **1. Create a Virtual Environment**

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

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

This will install:

* `numpy` – Numerical computation
* `matplotlib` – Visualizations
* `pytest` (optional) – Testing

### **3. Verify Installation**

```bash
python -c "import numpy, matplotlib; print('✓ Dependencies OK!')"
```

---

## Prepare Input Data

### **Required File: `data/coordenadas.csv`**

Format:

```csv
cep,latitude,longitude
82821020,-25.4524871,-49.2925963
80050370,-25.4376831,-49.2729254
...
```

**IMPORTANT:**

* Unibrasil ZIP code (`82821020`) **MUST** be present
* No extra spaces
* Comma as separator

### **Optional File: `data/ventos.json`**

Format:

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

## Run the System

### **Quick Test (10 generations):**

```bash
python main.py coordenadas.csv --gen 10 --pop 20
```

### **Default Execution (200 generations, no wind):**

```bash
python main.py coordenadas.csv
```

### **Full Execution (WITH wind):**

```bash
python main.py coordenadas.csv --wind ventos.json --gen 200 --pop 150
```

### **Long Execution (best results):**

```bash
python main.py coordenadas.csv --wind ventos.json --gen 500 --pop 300 --seed 42
```

---

## Check Results

After execution, you will find in `output/`:

```
output/
├── rota_saida.csv              ← FILE TO SUBMIT
├── distribuicao_ventos.png     ← Wind distribution chart
├── mapa_rota.png               ← Route map
└── estatisticas_rota.png       ← Detailed statistics
```

---

## Validation Checklist

Run BEFORE submitting:

```bash
# 1. Data files present?
ls -la data/
# Should show: coordenadas.csv, ventos.json (optional)

# 2. Virtual environment active?
which python
# Should show: .../venv/bin/python or ...\venv\Scripts\python

# 3. Full execution without errors?
python main.py coordenadas.csv --wind ventos.json --gen 100 --pop 100

# 4. Output files generated?
ls -la output/
# Should show: 4 files (.csv + 3 .png)

# 5. Validation passed?
# See in terminal:
#  REQUIREMENTS VALIDATION:
#    • Closed Route (Start/End Unibrasil): ✔ OK
#    • All ZIP Codes Visited: ✔ OK
#    • Within Deadline (7 days): ✔ OK
#    • Valid Speeds (36–96, multiple of 4): ✔ OK
#    • Valid Time Window (6 a.m.–7 p.m.): ✔ OK
```

---

## Common Issues

### **"ModuleNotFoundError: No module named 'core'"**

**Cause:** Running from the wrong directory
**Solution:**

```bash
cd unibrasil-surveyor/  # Go to project root
python main.py coordenadas.csv
```

### **"FileNotFoundError: coordenadas.csv"**

**Cause:** File is not in `data/`
**Solution:**

```bash
ls data/  # Check contents
# If empty, add the file:
cp /your/path/coordenadas.csv data/
```

### **Poor convergence (<5% in 20 generations)**

**Cause:** Insufficient parameters
**Solution:**

```bash
python main.py coordenadas.csv --gen 400 --pop 250
```

### **"ImportError: cannot import name 'gerar_todos_graficos'"**

**Cause:** Incorrect import in `main.py`
**Solution:** Use the corrected `main.py` provided

---

## **Author**

* Arthur Damiao Mendes

---

**Version:** 1.3.2
**Year:** 2025
**Status:** ✅ Ready for use
