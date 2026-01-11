.PHONY: help setup build start stop clean test smoke-test baseline scalability pattern-detection analyze

# Default target
help:
	@echo "CEP Benchmark - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup              - Install Python dependencies"
	@echo "  make build              - Build Docker images"
	@echo "  make generate-data      - Generate sample datasets"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make start              - Start all services"
	@echo "  make stop               - Stop all services"
	@echo "  make restart            - Restart all services"
	@echo "  make logs               - Tail all service logs"
	@echo "  make clean              - Remove all containers and volumes"
	@echo ""
	@echo "Testing:"
	@echo "  make smoke-test         - Quick validation (1 minute)"
	@echo "  make test               - Run unit and integration tests"
	@echo ""
	@echo "Experiments:"
	@echo "  make baseline           - Run baseline performance tests"
	@echo "  make scalability        - Run scalability tests"
	@echo "  make pattern-detection  - Run pattern detection tests"
	@echo "  make all-experiments    - Run all experiments"
	@echo ""
	@echo "Analysis:"
	@echo "  make analyze            - Generate analysis and figures"
	@echo "  make tables             - Generate LaTeX tables"
	@echo "  make figures            - Generate figures"
	@echo ""
	@echo "Monitoring:"
	@echo "  make grafana            - Open Grafana in browser"
	@echo "  make prometheus         - Open Prometheus in browser"
	@echo ""

# Setup
setup:
	pip install -r requirements.txt
	@echo "✓ Python dependencies installed"

build:
	docker-compose build
	@echo "✓ Docker images built"

generate-data:
	python preprocessing/data_preprocessor.py --sample
	@echo "✓ Sample data generated"

# Infrastructure management
start:
	docker-compose up -d
	@echo "✓ Services started"
	@echo "Waiting for Kafka to be ready..."
	@sleep 30
	@echo "✓ Infrastructure ready"

stop:
	docker-compose down
	@echo "✓ Services stopped"

restart: stop start

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf results/*
	rm -rf data/processed/*
	@echo "✓ All containers and volumes removed"

# Testing
smoke-test:
	@echo "Running smoke test..."
	./experiments/run_baseline.sh --duration 1 --quick
	@echo "✓ Smoke test completed"

test:
	pytest tests/ -v --cov
	@echo "✓ Tests completed"

# Experiments
baseline:
	@echo "Running baseline performance tests..."
	./experiments/run_baseline.sh
	@echo "✓ Baseline tests completed"

scalability:
	@echo "Running scalability tests..."
	./experiments/run_scalability.sh
	@echo "✓ Scalability tests completed"

pattern-detection:
	@echo "Running pattern detection tests..."
	./experiments/run_pattern_detection.sh
	@echo "✓ Pattern detection tests completed"

all-experiments: baseline scalability pattern-detection
	@echo "✓ All experiments completed"

# Analysis
analyze:
	cd analysis && python performance_analyzer.py --all
	cd analysis && python statistical_tests.py --all
	cd analysis && python visualization.py --all-figures
	@echo "✓ Analysis completed"

tables:
	cd analysis && python performance_analyzer.py --all-tables
	@echo "✓ Tables generated in results/tables/"

figures:
	cd analysis && python visualization.py --all-figures
	@echo "✓ Figures generated in results/figures/"

# Monitoring
grafana:
	@echo "Opening Grafana..."
	@xdg-open http://localhost:3000 2>/dev/null || open http://localhost:3000 || echo "Please open http://localhost:3000 manually"

prometheus:
	@echo "Opening Prometheus..."
	@xdg-open http://localhost:9090 2>/dev/null || open http://localhost:9090 || echo "Please open http://localhost:9090 manually"

# Development
format:
	black engines/ preprocessing/ workload/ monitoring/ analysis/
	@echo "✓ Code formatted"

lint:
	flake8 engines/ preprocessing/ workload/ monitoring/ analysis/
	@echo "✓ Linting completed"

type-check:
	mypy engines/ preprocessing/ workload/ monitoring/ analysis/
	@echo "✓ Type checking completed"
