#!/bin/bash

##############################################################################
# Baseline Performance Experiment Runner
# Compares Faust vs Streamz at moderate load levels
##############################################################################

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$PROJECT_ROOT/results/baseline_$(date +%Y%m%d_%H%M%S)"
DURATION_MINUTES=30
REPLICATIONS=5
INPUT_RATES=(500 1000 1500 2000)
DATASET="iot"

# Parse arguments
QUICK_MODE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --duration)
            DURATION_MINUTES="$2"
            shift 2
            ;;
        --quick)
            QUICK_MODE=true
            DURATION_MINUTES=1
            REPLICATIONS=1
            INPUT_RATES=(1000)
            shift
            ;;
        --dataset)
            DATASET="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--duration MINUTES] [--quick] [--dataset iot|financial]"
            exit 1
            ;;
    esac
done

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "=================================================="
echo "Baseline Performance Experiment"
echo "=================================================="
echo "Duration: $DURATION_MINUTES minutes"
echo "Replications: $REPLICATIONS"
echo "Input rates: ${INPUT_RATES[@]}"
echo "Dataset: $DATASET"
echo "Results directory: $RESULTS_DIR"
echo "=================================================="

# Log configuration
cat > "$RESULTS_DIR/config.txt" <<EOF
Experiment: Baseline Performance Comparison
Date: $(date)
Duration: $DURATION_MINUTES minutes per run
Replications: $REPLICATIONS
Input Rates: ${INPUT_RATES[@]} events/second
Dataset: $DATASET
Quick Mode: $QUICK_MODE
EOF

# Function to run single experiment
run_experiment() {
    local engine=$1
    local rate=$2
    local replication=$3
    
    echo ""
    echo "=================================================="
    echo "Running: Engine=$engine, Rate=$rate eps, Rep=$replication/$REPLICATIONS"
    echo "=================================================="
    
    local exp_dir="$RESULTS_DIR/${engine}_${rate}eps_rep${replication}"
    mkdir -p "$exp_dir"
    
    # Start CEP engine
    echo "Starting $engine..."
    docker-compose up -d $engine
    
    # Wait for engine to be ready
    echo "Waiting for engine to start..."
    sleep 10
    
    # Start workload generator
    echo "Starting workload generator at $rate events/second..."
    docker-compose run --rm \
        -e INPUT_RATE=$rate \
        -e DATASET=$DATASET \
        -e DURATION_SECONDS=$((DURATION_MINUTES * 60)) \
        workload-generator \
        python event_generator.py --rate $rate --dataset $DATASET --duration $((DURATION_MINUTES * 60)) \
        > "$exp_dir/workload.log" 2>&1 &
    
    WORKLOAD_PID=$!
    
    # Run for specified duration
    echo "Running for $DURATION_MINUTES minutes..."
    
    # Collect metrics every 5 seconds
    local elapsed=0
    local interval=5
    while [ $elapsed -lt $((DURATION_MINUTES * 60)) ]; do
        # Query Prometheus for metrics
        curl -s "http://localhost:9090/api/v1/query?query=cep_throughput_events_per_second{engine=\"$engine\"}" \
            >> "$exp_dir/metrics_throughput.json"
        echo "" >> "$exp_dir/metrics_throughput.json"
        
        curl -s "http://localhost:9090/api/v1/query?query=cep_processing_latency_seconds{engine=\"$engine\"}" \
            >> "$exp_dir/metrics_latency.json"
        echo "" >> "$exp_dir/metrics_latency.json"
        
        curl -s "http://localhost:9090/api/v1/query?query=cep_memory_bytes{engine=\"$engine\"}" \
            >> "$exp_dir/metrics_memory.json"
        echo "" >> "$exp_dir/metrics_memory.json"
        
        curl -s "http://localhost:9090/api/v1/query?query=cep_cpu_usage_percent{engine=\"$engine\"}" \
            >> "$exp_dir/metrics_cpu.json"
        echo "" >> "$exp_dir/metrics_cpu.json"
        
        sleep $interval
        elapsed=$((elapsed + interval))
        
        # Progress indicator
        progress=$((elapsed * 100 / (DURATION_MINUTES * 60)))
        echo -ne "Progress: $progress% ($elapsed/${DURATION_MINUTES}m)\r"
    done
    
    echo ""
    echo "Experiment completed, collecting final metrics..."
    
    # Wait for workload to finish
    wait $WORKLOAD_PID || true
    
    # Export final Prometheus metrics
    python3 - <<PYTHON_SCRIPT
import requests
import json
from datetime import datetime

metrics = {}
engine = "$engine"
exp_dir = "$exp_dir"

# Query various metrics
queries = {
    'throughput': f'rate(cep_events_processed_total{{engine="{engine}"}}[5m])',
    'latency_p50': f'histogram_quantile(0.50, rate(cep_processing_latency_seconds_bucket{{engine="{engine}"}}[5m]))',
    'latency_p95': f'histogram_quantile(0.95, rate(cep_processing_latency_seconds_bucket{{engine="{engine}"}}[5m]))',
    'latency_p99': f'histogram_quantile(0.99, rate(cep_processing_latency_seconds_bucket{{engine="{engine}"}}[5m]))',
    'memory': f'cep_memory_bytes{{engine="{engine}"}}',
    'cpu': f'cep_cpu_usage_percent{{engine="{engine}"}}'
}

for name, query in queries.items():
    try:
        response = requests.get(
            'http://localhost:9090/api/v1/query',
            params={'query': query}
        )
        metrics[name] = response.json()
    except Exception as e:
        print(f"Error querying {name}: {e}")
        metrics[name] = None

# Save metrics
with open(f'{exp_dir}/final_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"Metrics saved to {exp_dir}/final_metrics.json")
PYTHON_SCRIPT
    
    # Stop engine
    echo "Stopping $engine..."
    docker-compose stop $engine
    
    # Clean up
    sleep 5
    
    echo "Experiment completed: $exp_dir"
}

# Main experiment loop
for rate in "${INPUT_RATES[@]}"; do
    for rep in $(seq 1 $REPLICATIONS); do
        # Test Faust
        run_experiment "faust" $rate $rep
        
        # Cool-down period
        echo "Cool-down period (30 seconds)..."
        sleep 30
        
        # Test Streamz
        run_experiment "streamz" $rate $rep
        
        # Cool-down period between replications
        if [ $rep -lt $REPLICATIONS ]; then
            echo "Cool-down period between replications (60 seconds)..."
            sleep 60
        fi
    done
done

echo ""
echo "=================================================="
echo "All experiments completed!"
echo "Results saved to: $RESULTS_DIR"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Analyze results: cd analysis && python performance_analyzer.py --input $RESULTS_DIR"
echo "2. Generate figures: cd analysis && python visualization.py --input $RESULTS_DIR"
echo "3. Run statistical tests: cd analysis && python statistical_tests.py --input $RESULTS_DIR"
