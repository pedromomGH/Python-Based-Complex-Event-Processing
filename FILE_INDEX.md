# File Index - CEP Benchmark Reproducibility Package

All files organized alphabetically with descriptions and usage instructions.

## 📋 Quick Reference

| File Type | Count | Purpose |
|-----------|-------|---------|
| Documentation | 5 | Setup guides, dataset info, manifests |
| Python Scripts | 7 | Data generation, preprocessing, analysis |
| Configuration | 6 | Docker, Prometheus, requirements |
| Sample Data | 2 | Test datasets (1000 events each) |
| Shell Scripts | 1 | Experiment automation |
| **TOTAL** | **24** | Complete reproducibility package |

---

## 📄 Documentation Files

### README.md
**Purpose**: Main documentation and setup guide  
**Use**: Start here for installation and quick start  
**Contains**:
- System requirements
- Installation instructions
- Quick start guide
- Usage examples
- Troubleshooting

**Quick Start**:
```bash
# First file to read!
cat README.md
```

---

### GETTING_STARTED.md
**Purpose**: Step-by-step getting started guide  
**Use**: Detailed walkthrough for new users  
**Contains**:
- What has been created
- Package contents overview
- Quick validation steps
- Customization guide
- Testing checklist

**Quick Start**:
```bash
# Read after README
cat GETTING_STARTED.md
```

---

### DATA_README.md
**Purpose**: Complete dataset documentation  
**Use**: Understanding data schemas and formats  
**Contains**:
- Dataset descriptions
- Schema definitions (IoT and Financial)
- Ground truth labels explanation
- Data quality notes
- Citation information

**Quick Start**:
```bash
# Essential for understanding the data
cat DATA_README.md
```

---

### MANIFEST.md
**Purpose**: Complete file listing with original structure  
**Use**: Reference for original directory organization  
**Contains**:
- Original directory tree
- File descriptions
- Size estimates
- Version information

---

### Makefile
**Purpose**: Convenience commands  
**Use**: Quick access to common operations  
**Contains**:
- Setup commands
- Test runners
- Analysis shortcuts
- Infrastructure management

**Quick Start**:
```bash
# See all available commands
make help

# Run smoke test
make smoke-test

# Generate all figures
make figures
```

---

## 🐍 Python Scripts

### 1. generate_sample_iot_data.py
**Purpose**: Generate sample IoT network intrusion dataset  
**Output**: `sample_iot_data.csv` (1000 events)  
**Features**:
- Network traffic simulation
- 15.5% anomaly rate
- Attack type distribution
- 37 features per event

**Usage**:
```bash
python generate_sample_iot_data.py
# Creates: sample_iot_data.csv
```

**Dependencies**: pandas, numpy

---

### 2. generate_sample_financial_data.py
**Purpose**: Generate sample financial transaction dataset  
**Output**: `sample_financial_data.csv` (1000 transactions)  
**Features**:
- PaySim-style transactions
- 2.1% fraud rate
- 5 transaction types
- Realistic amount distributions

**Usage**:
```bash
python generate_sample_financial_data.py
# Creates: sample_financial_data.csv
```

**Dependencies**: pandas, numpy

---

### 3. data_preprocessor.py
**Purpose**: Preprocess datasets for CEP streaming  
**Input**: Raw CSV files  
**Output**: Standardized JSONL files  
**Features**:
- Temporal normalization
- Schema standardization
- Anomaly score calculation (Isolation Forest)
- Format conversion

**Usage**:
```bash
# Process sample datasets
python data_preprocessor.py --sample

# Process custom dataset
python data_preprocessor.py --dataset iot \
  --input raw_data.csv \
  --output processed_data.jsonl
```

**Dependencies**: pandas, numpy, scikit-learn

---

### 4. faust_app.py
**Purpose**: Faust CEP engine implementation  
**Architecture**: Stateful stream processing  
**Features**:
- Complex pattern detection
- RocksDB state management
- Three pattern types:
  - Anomaly bursts (5+ events, score >0.8, 60s window)
  - High-value bursts (3+ txns >$5000, 30s window)
  - Fraud sequences (score >0.9)
- Prometheus metrics export

**Usage**:
```bash
# Run with Docker (recommended)
docker-compose up faust

# Or run directly
faust -A faust_app worker -l info
```

**Metrics Endpoint**: http://localhost:8001/metrics  
**Dependencies**: See `requirements_faust.txt`

---

### 5. streamz_app.py
**Purpose**: Streamz CEP engine implementation  
**Architecture**: Stateless high-throughput processing  
**Features**:
- Lightweight pipeline
- Minimal overhead
- In-memory pattern tracking
- Prometheus metrics export

**Usage**:
```bash
# Run with Docker (recommended)
docker-compose up streamz

# Or run directly
python streamz_app.py --dataset iot
```

**Metrics Endpoint**: http://localhost:8002/metrics  
**Dependencies**: See `requirements_streamz.txt`

---

### 6. event_generator.py
**Purpose**: Generate event streams for benchmarking  
**Features**:
- Configurable rate control
- Multiple dataset support
- Burst pattern generation
- Kafka integration

**Usage**:
```bash
# Generate IoT events at 1000 eps
python event_generator.py \
  --dataset iot \
  --rate 1000 \
  --duration 300

# Generate with burst pattern
python event_generator.py \
  --dataset financial \
  --rate 1000 \
  --burst \
  --burst-rate 5000
```

**Dependencies**: kafka-python

---

### 7. performance_analyzer.py
**Purpose**: Generate tables from experimental results  
**Outputs**:
- Table 1: Baseline Performance Comparison
- Table 2: Latency Percentile Distribution
- Table 3: Resource Utilization
- Table 4: Pattern Detection Performance

**Formats**: CSV, LaTeX, Markdown

**Usage**:
```bash
# Generate all tables
python performance_analyzer.py --all-tables

# Generate specific table
python performance_analyzer.py --table baseline

# Use latest results
python performance_analyzer.py --latest --all-tables
```

**Output Directory**: `results/tables/`  
**Dependencies**: pandas, numpy, scipy

---

### 8. visualization_figures.py
**Purpose**: Generate figures from paper  
**Outputs**:
- Figure 1: Throughput comparison
- Figure 2: Efficiency scaling
- Figure 3: Latency distribution
- Figure 4: Resource comparison
- Figure 5: Pattern detection accuracy

**Formats**: PNG (300dpi), PDF

**Usage**:
```bash
# Generate all figures
python visualization_figures.py --all-figures

# Generate specific figure
python visualization_figures.py --figure throughput
```

**Output Directory**: `results/figures/`  
**Dependencies**: matplotlib, seaborn, pandas, numpy

---

## ⚙️ Configuration Files

### docker-compose.yml
**Purpose**: Container orchestration  
**Services**:
- Kafka + Zookeeper
- Faust CEP engine
- Streamz CEP engine
- Prometheus monitoring
- Grafana visualization
- Workload generator

**Usage**:
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d faust

# View logs
docker-compose logs -f faust

# Stop all
docker-compose down
```

---

### prometheus_config.yml
**Purpose**: Prometheus scraping configuration  
**Scrape Targets**:
- Faust metrics (port 8001)
- Streamz metrics (port 8002)
- Self-monitoring (port 9090)

**Scrape Interval**: 5 seconds  
**Usage**: Mounted automatically by docker-compose

---

### prometheus_alerts.yml
**Purpose**: Performance alerting rules  
**Alerts**:
- High processing latency (>0.5s for 2min)
- Low throughput (<100 eps for 3min)
- High memory usage (>500MB for 5min)
- High CPU usage (>80% for 5min)

**Usage**: Loaded automatically by Prometheus

---

### requirements.txt
**Purpose**: Main Python dependencies  
**Use**: Local development and testing  
**Contains**:
- Core libraries (pandas, numpy)
- Analysis tools (scipy, matplotlib)
- All dependencies for all scripts

**Usage**:
```bash
pip install -r requirements.txt
```

---

### requirements_faust.txt
**Purpose**: Faust-specific dependencies  
**Contains**:
- faust-streaming==0.10.4
- prometheus-client==0.18.0
- psutil==5.9.5
- python-rocksdb==0.7.0

**Usage**:
```bash
# Used automatically in Dockerfile_faust
pip install -r requirements_faust.txt
```

---

### requirements_streamz.txt
**Purpose**: Streamz-specific dependencies  
**Contains**:
- streamz==0.6.4
- kafka-python==2.0.2
- prometheus-client==0.18.0
- psutil==5.9.5

**Usage**:
```bash
# Used automatically in Dockerfile_streamz
pip install -r requirements_streamz.txt
```

---

### Dockerfile_faust
**Purpose**: Container image for Faust engine  
**Base**: python:3.11-slim  
**Includes**:
- RocksDB dependencies
- Faust and dependencies
- Application code

**Usage**:
```bash
# Build manually
docker build -f Dockerfile_faust -t cep-faust .

# Or use docker-compose
docker-compose build faust
```

---

### Dockerfile_streamz
**Purpose**: Container image for Streamz engine  
**Base**: python:3.11-slim  
**Includes**:
- Streamz and dependencies
- Application code

**Usage**:
```bash
# Build manually
docker build -f Dockerfile_streamz -t cep-streamz .

# Or use docker-compose
docker-compose build streamz
```

---

## 🔨 Shell Scripts

### run_baseline_experiments.sh
**Purpose**: Run baseline performance experiments  
**Features**:
- Multiple input rates (500-2000 eps)
- 5 replications per configuration
- Automated metric collection
- Progress tracking

**Usage**:
```bash
# Full baseline run (2-3 hours)
./run_baseline_experiments.sh

# Quick test (5 minutes)
./run_baseline_experiments.sh --quick

# Custom duration
./run_baseline_experiments.sh --duration 10
```

**Output**: `results/baseline_TIMESTAMP/`

---

## 📊 Sample Data Files

### sample_iot_data.csv
**Size**: ~528 KB (541,482 bytes)  
**Records**: 1,000 IoT network events  
**Features**: 37 fields  
**Anomalies**: 155 (15.5%)  
**Attack Types**: Mirai, BASHLITE, Scan, DDoS, Overflow

**Schema**:
- timestamp, device_id, event_type
- src_ip, dst_ip, src_port, dst_port
- packet_size, packet_count, flow_duration
- bytes_sent, bytes_received
- label, anomaly_score, attack_type
- 20 statistical features

**Usage**:
- Quick testing and validation
- Smoke tests
- Development

---

### sample_financial_data.csv
**Size**: ~186 KB (190,934 bytes)  
**Records**: 1,000 financial transactions  
**Features**: 15 fields  
**Fraud**: 21 (2.1%)  
**Transaction Types**: PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN

**Schema**:
- timestamp, step, type, amount
- nameOrig, oldbalanceOrg, newbalanceOrig
- nameDest, oldbalanceDest, newbalanceDest
- isFraud, isFlaggedFraud, fraud_score
- Derived features (balance changes, ratios)

**Usage**:
- Quick testing and validation
- Pattern detection testing
- Development

---

## 🔄 Workflow Examples

### Complete Setup
```bash
# 1. Generate sample data
python generate_sample_iot_data.py
python generate_sample_financial_data.py

# 2. Start infrastructure
docker-compose up -d kafka zookeeper prometheus grafana

# 3. Start CEP engines
docker-compose up -d faust streamz

# 4. Generate workload
python event_generator.py --dataset iot --rate 1000 --duration 60

# 5. View metrics
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
```

### Quick Validation
```bash
# 1. Generate data (if not exists)
python generate_sample_iot_data.py

# 2. Run smoke test
./run_baseline_experiments.sh --quick

# 3. Generate results
python performance_analyzer.py --latest --all-tables
python visualization_figures.py --all-figures
```

### Full Experiment
```bash
# 1. Ensure data exists
ls -lh sample_*.csv

# 2. Run full baseline
./run_baseline_experiments.sh

# 3. Analyze results
python performance_analyzer.py --input results/baseline_TIMESTAMP/
python visualization_figures.py --output results/figures/
```

---

## 📦 File Dependencies

```
Docker Environment:
├── docker-compose.yml
│   ├── Dockerfile_faust
│   │   └── requirements_faust.txt
│   └── Dockerfile_streamz
│       └── requirements_streamz.txt
│
Data Generation:
├── generate_sample_iot_data.py → sample_iot_data.csv
├── generate_sample_financial_data.py → sample_financial_data.csv
└── data_preprocessor.py → processed JSONL files
│
Experimentation:
├── run_baseline_experiments.sh
│   ├── docker-compose.yml
│   ├── event_generator.py
│   └── prometheus_config.yml
│
Analysis:
├── performance_analyzer.py → Tables (CSV, LaTeX, MD)
└── visualization_figures.py → Figures (PNG, PDF)
│
Monitoring:
├── prometheus_config.yml
├── prometheus_alerts.yml
└── faust_app.py / streamz_app.py (metrics export)
```

---

## 🎯 Quick Command Reference

```bash
# Installation
pip install -r requirements.txt
docker-compose build

# Data Generation
python generate_sample_iot_data.py
python generate_sample_financial_data.py

# Infrastructure
docker-compose up -d                    # Start all
docker-compose logs -f faust            # View logs
docker-compose down                     # Stop all

# Experiments
./run_baseline_experiments.sh           # Full run
./run_baseline_experiments.sh --quick   # Quick test

# Analysis
python performance_analyzer.py --all-tables
python visualization_figures.py --all-figures

# Monitoring
open http://localhost:3000              # Grafana
open http://localhost:9090              # Prometheus
```

---

## 📝 Notes

1. **All files are in root directory** - Easy to find and use
2. **No subdirectories** - Simple structure for GitHub
3. **Unique names** - No filename conflicts
4. **Self-contained** - Each component works independently
5. **Well-documented** - Every file has clear purpose

---

**Last Updated**: 2025-01-11  
**Total Files**: 24  
**Total Size**: ~850 KB (excluding sample data)  
**With Sample Data**: ~1.6 MB
