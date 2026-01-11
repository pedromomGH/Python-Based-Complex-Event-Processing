# CEP Engine Performance Comparison: Reproducibility Package

This repository contains the complete reproducibility package for the paper "Performance Comparison of Python-Based Complex Event Processing Engines: Faust versus Streamz".

## Citation

If you use this code or data in your research, please cite:

```
Abbasi, M., Cardoso, F., Váz, P., Silva, J., Sá, F., & Martins, P. (2025).
Performance Comparison of Python-Based Complex Event Processing Engines: Faust versus Streamz.
[Journal Name], 1(1), Article 0.
```

## Overview

This package provides:
- Complete Docker-based experimental environment
- Faust and Streamz CEP engine implementations
- Data preprocessing and anomaly injection pipelines
- Workload generation and load control systems
- Prometheus/Grafana monitoring infrastructure
- Performance analysis and statistical testing scripts
- Automated experiment runners
- Sample datasets for validation

## System Requirements

### Hardware
- **Minimum**: 4 CPU cores, 8GB RAM, 20GB disk space
- **Recommended** (for full experiments): 8 CPU cores, 16GB RAM, 50GB disk space
- **Paper Configuration**: Intel Xeon E5-2686 v4 (8 cores), 16GB RAM, 1TB NVMe SSD

### Software
- Docker Engine 20.10+ and Docker Compose 2.0+
- Python 3.11+ (for local development/analysis)
- GNU Make (optional, for convenience commands)
- Linux OS (tested on Ubuntu 22.04)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/cep-benchmark.git
cd cep-benchmark

# Generate sample data
python generate_sample_iot_data.py
python generate_sample_financial_data.py

# Build Docker images
docker-compose build
```

### 2. Start Infrastructure

```bash
# Start Kafka, Prometheus, Grafana
docker-compose up -d kafka zookeeper prometheus grafana

# Wait for Kafka to be ready (about 30 seconds)
docker-compose logs -f kafka | grep "started (kafka.server.KafkaServer)"
```

### 3. Run Quick Test

```bash
# Run baseline performance test (5 minutes)
./run_baseline_experiments.sh --quick

# View results
python performance_analyzer.py --latest
```

### 4. Access Monitoring

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Full Experiment Reproduction

### Step 1: Data Preparation

```bash
# Download full datasets (if not using samples)
cd data
wget https://ieee-dataport.org/documents/iot-network-intrusion-dataset
wget https://www.kaggle.com/datasets/ealaxi/paysim1

# Preprocess datasets
cd ../preprocessing
python data_preprocessor.py --dataset iot --input ../data/iot_raw.csv
python data_preprocessor.py --dataset financial --input ../data/financial_raw.csv
python anomaly_injector.py --dataset iot
python anomaly_injector.py --dataset financial
```

### Step 2: Baseline Performance Tests

```bash
# Run baseline comparison (30 minutes per engine)
./experiments/run_baseline.sh

# Results will be saved to: results/baseline_TIMESTAMP/
```

### Step 3: Scalability Tests

```bash
# Run scalability tests with increasing load (2-3 hours)
./experiments/run_scalability.sh

# Results will be saved to: results/scalability_TIMESTAMP/
```

### Step 4: Pattern Detection Tests (Faust only)

```bash
# Run pattern detection accuracy tests (1-2 hours)
./experiments/run_pattern_detection.sh

# Results will be saved to: results/pattern_detection_TIMESTAMP/
```

### Step 5: Generate Analysis and Figures

```bash
cd analysis

# Generate all tables from paper
python performance_analyzer.py --generate-tables

# Generate all figures
python visualization.py --generate-figures

# Run statistical tests
python statistical_tests.py --all

# Output will be in: results/analysis_TIMESTAMP/
```

## Repository Structure

All files are in the root directory for simplicity:

```
cep-benchmark/
├── README.md                              # This file - main documentation
├── GETTING_STARTED.md                     # Step-by-step getting started guide
├── FILE_INDEX.md                          # Complete file index with descriptions
├── DATA_README.md                         # Dataset documentation
├── MANIFEST.md                            # Original structure reference
├── Makefile                               # Convenience commands
│
├── docker-compose.yml                     # Container orchestration
├── Dockerfile_faust                       # Faust engine container
├── Dockerfile_streamz                     # Streamz engine container
│
├── requirements.txt                       # Main Python dependencies
├── requirements_faust.txt                 # Faust-specific dependencies
├── requirements_streamz.txt               # Streamz-specific dependencies
│
├── prometheus_config.yml                  # Prometheus configuration
├── prometheus_alerts.yml                  # Alert rules
│
├── generate_sample_iot_data.py           # IoT sample data generator
├── generate_sample_financial_data.py     # Financial sample data generator
├── sample_iot_data.csv                   # Sample IoT dataset (1000 events)
├── sample_financial_data.csv             # Sample financial dataset (1000 txns)
│
├── data_preprocessor.py                  # Data preprocessing pipeline
├── faust_app.py                          # Faust CEP engine implementation
├── streamz_app.py                        # Streamz CEP engine implementation
├── event_generator.py                    # Workload generator
│
├── run_baseline_experiments.sh           # Baseline experiment runner
├── performance_analyzer.py               # Analysis and table generation
└── visualization_figures.py              # Figure generation
```

**Note**: Results and figures are generated in `results/` directory (not included in repository)

## Configuration

### Experiment Parameters

Edit `experiments/experiment_config.yaml`:

```yaml
baseline:
  duration_minutes: 30
  input_rates: [500, 1000, 1500, 2000]
  replications: 5

scalability:
  duration_minutes: 30
  input_rates: [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
  replications: 5

pattern_detection:
  duration_minutes: 30
  input_rates: [500, 1000, 1500, 2000, 2500, 3000]
  replications: 5
  anomaly_injection_rate: 0.15
```

### Engine Configuration

**Faust** (`engines/faust_app/config.py`):
- Broker: Kafka connection settings
- State: RocksDB backend configuration
- Processing: Window sizes, commit intervals
- Parallelism: Number of workers

**Streamz** (`engines/streamz_app/config.py`):
- Broker: Kafka connection settings
- Buffer: In-memory queue sizes
- Polling: Consumer polling intervals
- Backpressure: Max queue depth

## Monitoring and Observability

### Grafana Dashboards

Access Grafana at http://localhost:3000 (default: admin/admin)

Available dashboards:
1. **Executive Summary**: High-level performance overview
2. **Faust Detailed**: Faust-specific metrics and state
3. **Streamz Detailed**: Streamz-specific metrics
4. **Comparative View**: Side-by-side comparison
5. **Infrastructure**: Kafka and system metrics

### Prometheus Metrics

Exposed metrics include:
- `cep_events_processed_total`: Total events processed
- `cep_processing_latency_seconds`: Latency histogram
- `cep_throughput_events_per_second`: Current throughput
- `cep_pattern_detections_total`: Pattern matches (Faust)
- `cep_memory_bytes`: Memory consumption
- `cep_cpu_usage_percent`: CPU utilization

### Logs

View engine logs:
```bash
# Faust logs
docker-compose logs -f faust

# Streamz logs
docker-compose logs -f streamz

# All services
docker-compose logs -f
```

## Data Documentation

### Sample Datasets

Small sample datasets are included for quick testing:
- `data/sample_iot_data.csv`: 1,000 IoT events
- `data/sample_financial_data.csv`: 1,000 financial transactions

### Full Datasets

For full reproduction, download:

1. **IoT Network Intrusion Dataset**
   - Source: IEEE Dataport
   - DOI: 10.21227/q70p-q449
   - Size: 583,485 events
   - License: CC BY 4.0

2. **PaySim Financial Dataset**
   - Source: Kaggle/Original paper
   - Size: 6,362,620 transactions
   - License: CC BY-SA 4.0

### Preprocessing Pipeline

The preprocessing applies:
1. Temporal normalization (preserving ordering)
2. Schema standardization
3. Anomaly score calculation (Isolation Forest)
4. Format conversion (CSV → JSON streaming)

Ground truth labels are preserved from original datasets and augmented with:
- Anomaly scores from Isolation Forest (contamination=0.1)
- Synthetic pattern injections at controlled rates
- Temporal markers for pattern evaluation

## Performance Analysis

### Metrics Collected

1. **Throughput**
   - Sustained throughput (events/sec)
   - Peak throughput
   - Processing efficiency (%)

2. **Latency**
   - P50, P75, P90, P95, P99 percentiles
   - Maximum latency
   - Latency distribution

3. **Resource Utilization**
   - CPU usage (mean, peak, stddev)
   - Memory consumption
   - Network I/O

4. **Pattern Detection** (Faust only)
   - Precision, Recall, F1-Score
   - False positive rate
   - Detection latency

### Statistical Analysis

All comparisons include:
- Paired t-tests (or Wilcoxon for non-normal distributions)
- Effect sizes (Cohen's d)
- 95% confidence intervals
- Bonferroni correction for multiple comparisons

### Reproducing Paper Tables

```bash
cd analysis

# Table 1: Baseline Performance Comparison
python performance_analyzer.py --table baseline

# Table 2: Latency Percentile Distribution
python performance_analyzer.py --table latency

# Table 3: Resource Utilization
python performance_analyzer.py --table resources

# Table 4: Pattern Detection Performance
python performance_analyzer.py --table patterns

# All tables
python performance_analyzer.py --all-tables
```

### Reproducing Paper Figures

```bash
cd analysis

# Figure 1: Throughput comparison
python visualization.py --figure throughput

# Figure 2: Efficiency scaling
python visualization.py --figure efficiency

# All figures
python visualization.py --all-figures
```

## Customization

### Adding New Patterns

Edit `engines/faust_app/patterns.py` to add new detection logic:

```python
@app.agent(events_topic)
async def detect_custom_pattern(stream):
    async for event in stream.group_by(lambda e: e['device_id']):
        # Your pattern detection logic
        if condition_met(event):
            await pattern_topic.send(value={'pattern': 'custom', ...})
```

### Custom Datasets

1. Prepare CSV with required fields:
   - `timestamp`: Event timestamp
   - `entity_id`: Device/account ID
   - `event_type`: Event classification
   - `anomaly_score`: Anomaly indicator (0-1)

2. Run preprocessor:
```bash
python preprocessing/data_preprocessor.py --custom \
    --input your_data.csv \
    --output processed_data.json
```

### Different Load Profiles

Edit `workload/config.yaml` to define custom workload patterns:

```yaml
custom_profile:
  type: stepped
  initial_rate: 1000
  step_size: 500
  step_duration_seconds: 300
  max_rate: 5000
```

## Troubleshooting

### Common Issues

**Kafka not starting:**
```bash
# Check logs
docker-compose logs kafka

# Reset Kafka state
docker-compose down -v
docker-compose up -d kafka
```

**Out of memory:**
```bash
# Increase Docker memory limit
# Edit Docker Desktop settings or /etc/docker/daemon.json

# Reduce concurrent load
# Edit experiments/experiment_config.yaml
# Reduce input_rates or replications
```

**Port conflicts:**
```bash
# Check what's using ports
lsof -i :9092  # Kafka
lsof -i :9090  # Prometheus
lsof -i :3000  # Grafana

# Change ports in docker-compose.yml if needed
```

See `docs/TROUBLESHOOTING.md` for more issues and solutions.

## Performance Optimization

### System Tuning

For production-like performance:

```bash
# Disable CPU frequency scaling
sudo cpupower frequency-set -g performance

# Optimize network buffers
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728

# Reduce swappiness
sudo sysctl -w vm.swappiness=1

# Disable transparent huge pages
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
```

### Docker Optimization

Edit `/etc/docker/daemon.json`:

```json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
```

## Validation and Testing

### Unit Tests

```bash
# Run all unit tests
python -m pytest tests/

# Run specific test suite
python -m pytest tests/test_preprocessing.py
python -m pytest tests/test_patterns.py
```

### Integration Tests

```bash
# Run integration tests
./tests/integration/test_end_to_end.sh
```

### Smoke Test

Quick validation of setup:

```bash
# Run 1-minute smoke test
make smoke-test

# Or manually:
./experiments/run_baseline.sh --duration 1 --quick
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This code is released under the MIT License. See LICENSE file for details.

The datasets have their own licenses:
- IoT Dataset: CC BY 4.0
- PaySim Dataset: CC BY-SA 4.0

## Support

For questions or issues:
- Open an issue on GitHub
- Contact: pedromom@estgv.ipv.pt

## Acknowledgments

This research was supported by:
- Research Center in Digital Services, Polytechnic Institute of Viseu
- Polytechnic Institute of Santarém
- Applied Research Institute, Polytechnic Institute of Coimbra

## Version History

- v1.0.0 (2025-01): Initial release with paper publication
- v1.1.0: Added support for custom datasets
- v1.2.0: Enhanced monitoring dashboards

## Related Publications

1. Abbasi et al. (2025). Performance Comparison of Python-Based CEP Engines.
2. [Additional related papers]

---

**Last Updated**: January 2025
**Maintainer**: Pedro Martins (pedromom@estgv.ipv.pt)
