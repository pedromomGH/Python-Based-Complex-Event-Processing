# CEP Benchmark Reproducibility Package - File Manifest

Generated: 2025-01-11
Version: 1.0.0

## Repository Structure

```
cep-benchmark/
├── README.md                                 [Main documentation and setup guide]
├── LICENSE                                   [MIT License]
├── .gitignore                               [Git ignore rules]
├── Makefile                                 [Convenience commands]
├── docker-compose.yml                       [Container orchestration]
├── requirements.txt                         [Python dependencies]
│
├── config/                                  [Configuration files]
│   ├── kafka/                              [Kafka broker configuration]
│   ├── prometheus/                         [Monitoring configuration]
│   │   ├── prometheus.yml                  [Prometheus scraping config]
│   │   └── alerts.yml                      [Alerting rules]
│   └── grafana/                           [Grafana dashboards]
│       ├── provisioning/                   [Auto-provisioning]
│       └── dashboards/                     [Dashboard JSON files]
│
├── data/                                   [Datasets]
│   ├── README.md                           [Data documentation]
│   ├── generate_iot_sample.py             [IoT sample generator]
│   ├── generate_financial_sample.py       [Financial sample generator]
│   ├── sample_iot_data.csv                [Sample IoT events (1000)]
│   ├── sample_financial_data.csv          [Sample financial transactions (1000)]
│   ├── raw/                               [Raw datasets (not included)]
│   └── processed/                         [Processed JSONL files]
│
├── preprocessing/                          [Data preprocessing]
│   ├── data_preprocessor.py               [Main preprocessing script]
│   ├── anomaly_injector.py                [Synthetic anomaly injection]
│   └── utils.py                           [Helper functions]
│
├── engines/                               [CEP engine implementations]
│   ├── faust_app/                        [Faust implementation]
│   │   ├── app.py                        [Main application]
│   │   ├── patterns.py                   [Pattern detection logic]
│   │   ├── config.py                     [Configuration]
│   │   ├── Dockerfile                    [Container image]
│   │   └── requirements.txt              [Python dependencies]
│   │
│   └── streamz_app/                      [Streamz implementation]
│       ├── app.py                        [Main application]
│       ├── config.py                     [Configuration]
│       ├── Dockerfile                    [Container image]
│       └── requirements.txt              [Python dependencies]
│
├── workload/                              [Workload generation]
│   ├── event_generator.py                [Event stream generator]
│   ├── load_controller.py                [Load scaling controller]
│   ├── config.yaml                       [Workload profiles]
│   └── Dockerfile                        [Container image]
│
├── monitoring/                            [Observability]
│   ├── metrics_collector.py              [Custom metrics]
│   ├── prometheus_exporter.py            [Prometheus integration]
│   └── dashboard_templates/              [Grafana dashboards]
│       ├── executive_summary.json
│       ├── faust_detailed.json
│       ├── streamz_detailed.json
│       └── comparative_view.json
│
├── analysis/                              [Results processing]
│   ├── performance_analyzer.py            [Performance metrics analysis]
│   ├── statistical_tests.py              [Statistical analysis]
│   ├── visualization.py                  [Figure generation]
│   └── report_generator.py               [LaTeX table generation]
│
├── experiments/                           [Experiment runners]
│   ├── run_baseline.sh                   [Baseline tests]
│   ├── run_scalability.sh                [Scalability tests]
│   ├── run_pattern_detection.sh          [Pattern detection tests]
│   ├── run_all.sh                        [Run all experiments]
│   └── experiment_config.yaml            [Experiment parameters]
│
├── tests/                                 [Unit and integration tests]
│   ├── unit/
│   │   ├── test_preprocessing.py
│   │   ├── test_faust_patterns.py
│   │   └── test_streamz_pipeline.py
│   ├── integration/
│   │   ├── test_end_to_end.sh
│   │   └── test_workload_generation.py
│   └── conftest.py                       [Pytest configuration]
│
├── docs/                                  [Additional documentation]
│   ├── ARCHITECTURE.md                   [System architecture]
│   ├── METRICS.md                        [Metric definitions]
│   ├── TROUBLESHOOTING.md                [Common issues]
│   ├── CUSTOMIZATION.md                  [Extending the benchmark]
│   └── API.md                            [API documentation]
│
└── results/                               [Experiment results (generated)]
    ├── baseline_TIMESTAMP/               [Baseline experiment results]
    ├── scalability_TIMESTAMP/            [Scalability test results]
    ├── pattern_detection_TIMESTAMP/      [Pattern detection results]
    ├── figures/                          [Generated figures]
    ├── tables/                           [Generated tables]
    └── analysis/                         [Statistical analysis output]
```

## File Descriptions

### Root Files

- **README.md**: Comprehensive setup and usage guide
- **LICENSE**: MIT license for the code
- **Makefile**: Convenience commands for common operations
- **docker-compose.yml**: Orchestrates all services (Kafka, CEP engines, monitoring)
- **requirements.txt**: Python dependencies for local development

### Configuration (`config/`)

- **kafka/**: Kafka broker configuration files
- **prometheus/prometheus.yml**: Metrics collection configuration
- **prometheus/alerts.yml**: Performance alert rules
- **grafana/**: Dashboard definitions and provisioning

### Data (`data/`)

- **README.md**: Detailed data documentation and schemas
- **generate_*_sample.py**: Scripts to create sample datasets
- **sample_*.csv**: Pre-generated sample datasets (1000 events each)
- **raw/**: Directory for full datasets (not included, download separately)
- **processed/**: JSONL format datasets ready for streaming

### Preprocessing (`preprocessing/`)

- **data_preprocessor.py**: Main data preprocessing pipeline
  - Temporal normalization
  - Schema standardization
  - Anomaly score calculation (Isolation Forest)
  - Format conversion (CSV → JSONL)

- **anomaly_injector.py**: Synthetic pattern injection
  - Controlled anomaly insertion
  - Pattern labeling for evaluation
  - Ground truth generation

### CEP Engines (`engines/`)

#### Faust (`engines/faust_app/`)

- **app.py**: Main Faust application with pattern detection
  - Stateful stream processing
  - Complex event pattern detection
  - Prometheus metrics export
  
- **patterns.py**: Pattern detection implementations
  - Anomaly burst detection
  - High-value transaction detection
  - Fraud sequence detection
  
- **config.py**: Configuration management
- **Dockerfile**: Container image definition
- **requirements.txt**: Faust-specific dependencies

#### Streamz (`engines/streamz_app/`)

- **app.py**: Main Streamz application
  - Stateless stream processing
  - High-throughput pipeline
  - Prometheus metrics export
  
- **config.py**: Configuration management
- **Dockerfile**: Container image definition
- **requirements.txt**: Streamz-specific dependencies

### Workload Generation (`workload/`)

- **event_generator.py**: Main event stream generator
  - Configurable rate control
  - Multiple dataset support
  - Burst pattern generation
  
- **load_controller.py**: Dynamic load adjustment
  - Stepped load profiles
  - Ramp-up/ramp-down patterns
  - Load shedding simulation

### Monitoring (`monitoring/`)

- **metrics_collector.py**: Custom metric collection
- **prometheus_exporter.py**: Prometheus integration
- **dashboard_templates/**: Pre-configured Grafana dashboards

### Analysis (`analysis/`)

- **performance_analyzer.py**: Main analysis tool
  - Table generation (Tables 1-4 from paper)
  - Metric extraction and aggregation
  - LaTeX/CSV/Markdown export
  
- **statistical_tests.py**: Statistical analysis
  - Paired t-tests and Wilcoxon tests
  - Cohen's d effect size calculation
  - Confidence interval computation
  
- **visualization.py**: Figure generation
  - Throughput comparison (Figure 1)
  - Efficiency scaling (Figure 2)
  - Latency distribution
  - Resource comparison
  - Pattern detection accuracy
  
- **report_generator.py**: Automated report generation

### Experiments (`experiments/`)

- **run_baseline.sh**: Baseline performance comparison
  - Multiple input rates (500-2000 eps)
  - 5 replications per configuration
  - Automated metric collection
  
- **run_scalability.sh**: Scalability testing
  - Graduated load increases (500-5000 eps)
  - Saturation point identification
  - Efficiency degradation analysis
  
- **run_pattern_detection.sh**: Pattern detection evaluation
  - Accuracy vs. load analysis
  - False positive/negative rates
  - Faust-specific testing
  
- **experiment_config.yaml**: Centralized configuration

### Tests (`tests/`)

- **unit/**: Unit tests for components
- **integration/**: End-to-end integration tests
- **conftest.py**: Pytest fixtures and configuration

### Documentation (`docs/`)

- **ARCHITECTURE.md**: Detailed system architecture
- **METRICS.md**: Complete metric definitions
- **TROUBLESHOOTING.md**: Common issues and solutions
- **CUSTOMIZATION.md**: Guide to extending the benchmark
- **API.md**: API documentation for components

### Results (`results/`)

Generated during experiments, not included in repository:

- **baseline_*/**: Baseline experiment data
- **scalability_*/**: Scalability test data
- **pattern_detection_*/**: Pattern detection results
- **figures/**: PNG and PDF figures
- **tables/**: CSV, LaTeX, and Markdown tables
- **analysis/**: Statistical analysis outputs

## Key Features

### Reproducibility

✅ Complete source code for all components
✅ Containerized environment (Docker Compose)
✅ Deterministic data preprocessing
✅ Fixed random seeds for reproducibility
✅ Comprehensive configuration documentation
✅ Automated experiment runners
✅ Statistical analysis scripts

### Extensibility

✅ Modular architecture
✅ Well-documented APIs
✅ Configurable parameters
✅ Custom pattern support
✅ Additional dataset integration
✅ Plugin-based monitoring

### Validation

✅ Unit tests for core components
✅ Integration tests for workflows
✅ Sample datasets for quick validation
✅ Smoke test capabilities
✅ CI/CD compatible structure

## File Sizes (Approximate)

```
Source Code:         ~50 KB
Configuration:       ~20 KB
Documentation:       ~100 KB
Sample Data:         ~2 MB
Docker Images:       ~2 GB (when built)
Full Datasets:       ~1 GB (download separately)
Results per Run:     ~50-200 MB
```

## Dependencies

### System Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for local development)
- 8 GB RAM minimum (16 GB recommended)
- 20 GB disk space (50 GB for full experiments)

### Python Packages

See `requirements.txt` for complete list. Key dependencies:

- **CEP Engines**: faust-streaming, streamz, kafka-python
- **Data Processing**: pandas, numpy, scikit-learn
- **Monitoring**: prometheus-client, psutil
- **Analysis**: scipy, statsmodels
- **Visualization**: matplotlib, seaborn

### Infrastructure

- **Kafka**: Confluent Platform 7.4.0
- **Prometheus**: v2.47.0
- **Grafana**: v10.1.0
- **Zookeeper**: Confluent 7.4.0

## Version Information

- **Package Version**: 1.0.0
- **Python**: 3.11.4
- **Faust**: 1.10.4
- **Streamz**: 0.6.4
- **Kafka**: 7.4.0

## Checksums

MD5 checksums for verification (sample data):

```
sample_iot_data.csv:        [generated]
sample_financial_data.csv:  [generated]
```

## Updates and Maintenance

This manifest reflects the initial release. For updates:

- Check GitHub releases
- Review CHANGELOG.md
- Monitor version tags

## Support

For questions or issues:

- **GitHub Issues**: https://github.com/yourusername/cep-benchmark/issues
- **Email**: pedromom@estgv.ipv.pt
- **Documentation**: See docs/ directory

---

**Last Updated**: 2025-01-11
**Maintainer**: Pedro Martins
**License**: MIT
