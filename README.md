# UNIBRASIL Surveyor

Route optimization system for an autonomous drone using a Genetic Algorithm.

## Project Description

UNIBRASIL Surveyor is a system designed to plan optimized routes for an autonomous drone that must photograph multiple ZIP codes (CEPs) in the city of Curitiba. The goal is to **minimize total cost**, measured by flight time and the number of recharging stops.

---

## System Objectives

1. **Minimize total flight time**
2. **Minimize the number of recharges**
3. **Respect all operational constraints**:

   * Battery autonomy
   * Operating time window (6 a.m.–7 p.m.)
   * 7-day deadline
   * Wind effects
   * Valid speed limits

---

## Project Structure

```
unibrasil-surveyor/
├── main.py                     # Main execution script
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
├── .gitignore                  # Git ignored files
│
├── data/                       # Input files
│   ├── coordenadas.csv         # ZIP codes and coordinates (provided by professor)
│   └── ventos.json             # Wind forecast (7 days)
│
├── core/                       # Main source code
│   ├── __init__.py
│   ├── config.py               # Configuration and parameters
│   ├── data_loader.py          # Data loading
│   ├── physics.py              # Drone physics (acceleration, wind)
│   ├── simulation.py           # Route simulation and fitness
│   ├── genetic_algorithm.py    # Genetic Algorithm
│   └── visualizacao.py         # Chart generation
│
├── output/                     # Generated files
│   ├── rota_saida.csv          # Final solution
│   ├── distribuicao_ventos.png # Wind distribution chart
│   ├── mapa_rota.png           # Route map
│   ├── estatisticas_rota.png   # Statistics
│   └── monitoramento_*.png     # GA evolution
│
└── tests/                      # Unit tests
    ├── __init__.py
    ├── test_data_loader.py
    ├── test_simulation.py
    └── test_genetic_algorithm.py
```

---

## Installation and Execution

### **Prerequisites**

* Python 3.8 or higher
* pip (Python package manager)

### **1. Clone / Extract the Project**

```bash
# If using a Git repository:
git clone <repository-url>
cd unibrasil-surveyor

# Or extract the provided ZIP
unzip unibrasil-surveyor.zip
cd unibrasil-surveyor
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Prepare Input Data**

Ensure the files are located in the `data/` directory:

```
data/
├── coordenadas.csv    # ZIP codes and coordinates (required)
└── ventos.json        # Wind forecast (optional)
```

### **4. Run the System**

**Basic execution (no wind):**

```bash
python main.py coordenadas.csv
```

**Full execution (with wind):**

```bash
python main.py coordenadas.csv --wind ventos.json
```

**Execution with custom parameters:**

```bash
python main.py coordenadas.csv \
    --wind ventos.json \
    --gen 300 \
    --pop 200 \
    --seed 42 \
    --out rota_final.csv
```

### **5. Available Parameters**

| Parameter | Description                        | Default          |
| --------- | ---------------------------------- | ---------------- |
| `arquivo` | CSV file with ZIP codes (required) | –                |
| `--wind`  | JSON file with wind data           | `ventos.json`    |
| `--pop`   | Population size                    | `150`            |
| `--gen`   | Number of generations              | `200`            |
| `--seed`  | Seed for reproducibility           | Random           |
| `--out`   | Output file name                   | `rota_saida.csv` |

**Examples:**

```bash
# Quick test (10 generations, small population)
python main.py coordenadas.csv --gen 10 --pop 20

# Execution with fixed seed (reproducible)
python main.py coordenadas.csv --seed 42

# Long execution for best results
python main.py coordenadas.csv --gen 500 --pop 300
```

---

## Generated Outputs

All files are saved in the `output/` directory:

### **1. rota_saida.csv**

CSV file with the detailed route. Format:

```csv
cep_inicial,lat_inicial,lon_inicial,dia,hora_inicial,velocidade,cep_final,lat_final,lon_final,pouso,hora_final
82821020,-25.4524871,-49.2925963,1,06:00:00,72,80050370,-25.4376831,-49.2729254,NO,06:12:34
...
```

### **2. Visualization Charts**

* **distribuicao_ventos.png**: Wind speed and direction by day
* **mapa_rota.png**: Route map (latitude × longitude)
* **estatisticas_rota.png**: Detailed statistics (landings, speeds, etc.)
* **monitoramento_completo.png**: Fitness evolution across generations

---

## System Configuration

### **Drone Parameters (`config.py`)**

```python
VELOCIDADE_MAXIMA = 96        # km/h
VELOCIDADE_MINIMA = 36        # km/h (10 m/s)
AUTONOMIA_BASE_SEG = 4650.0   # ~77.5 minutes (Curitiba factor: 0.93)
TEMPO_PARADA_SEG = 72         # 1 min 12 s per stop
TEMPO_RECARGA_SEG = 3600      # 1 hour
```

### **Genetic Algorithm Parameters**

```python
POP_SIZE = 150
CROSSOVER_RATE = 0.85
MUTATION_RATE_SWAP = 0.12
MUTATION_RATE_INVERSION = 0.08
MUTATION_RATE_2OPT = 0.05
ELITISM_COUNT = 5
TOURNAMENT_SIZE = 3
```

### **Fitness Function (Lexicographic Hierarchy)**

```python
FITNESS = Distance × 1_000_000   # Dominant factor (~87%)
        + Landings × 1_000       # Medium tie-break (~1%)
        + Time × 1               # Fine tie-break (~9%)
        + Penalties              # Severe violations (~3%)
```

**Guarantee:** 100 m of distance > 50 landings + 200,000 seconds

---

## Genetic Algorithm

### **Representation**

* **Chromosome:** ZIP code permutation + speed vector
* **Route:** [base, zip1, zip2, ..., zipN, base]
* **Speeds:** [v1, v2, ..., vN+1] (km/h, multiples of 4)

### **Operators**

1. **Selection:** Tournament (k = 3)
2. **Crossover:** Order Crossover (OX)
3. **Mutation:**

   * Swap
   * Inversion
   * 2-opt
4. **Elitism:** Preserves top 5 individuals

### **Anti-Stagnation Strategy**

* Detection every 20 generations
* Partial restart (30% new individuals)
* Hyper-mutation (40% rate)
* Local 2-opt search on elites

---

## Wind Consideration

### **Effect on Speed**

```
effective_speed = drone_speed + wind_component

wind_component = wind_speed × cos(relative_angle)
```

* **Tailwind (0°):** increases speed
* **Headwind (180°):** reduces speed
* **Crosswind (90°):** no direct effect

---

## Solution Validation

The system automatically validates:

1. ✓ Closed route (starts and ends at Unibrasil)
2. ✓ All ZIP codes visited exactly once
3. ✓ Within the 7-day deadline
4. ✓ Valid speeds (36–96 km/h, multiple of 4)
5. ✓ Valid operating hours (6 a.m.–7 p.m.)
6. ✓ Battery autonomy respected

---

## Tests

```bash
pytest tests/
pytest --cov=core tests/
pytest tests/test_simulation.py -v
```

---

## Result Interpretation

### **Fitness**

* **< 50,000,000** (≈50 ZIPs): Excellent
* **< 60,000,000**: Good
* **> 70,000,000**: Review parameters

---

## References

1. Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning.*
2. Laporte, G. (1992). *The Traveling Salesman Problem.*
3. Vincenty, T. (1975). *Geodesics on the Ellipsoid.*

---

## Authors

* Arthur Damiao Mendes

---

## License

This project is part of an academic assignment for the Cognitive Services course at Unibrasil.

---

**Version:** 1.3.2
**Year:** 2025
**Status:** ✅ Ready for use
