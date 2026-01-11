"""
Visualization Module for CEP Benchmark
Generates figures for the paper
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11


class BenchmarkVisualizer:
    """Creates visualizations from benchmark results"""
    
    def __init__(self, output_dir: str = 'results/figures'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_throughput_comparison(self):
        """Figure 1: Throughput comparison across input rates"""
        logger.info("Generating throughput comparison figure...")
        
        # Data from paper (Table and Figure 1)
        input_rates = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
        faust_throughput = [485, 920, 1380, 1850, 2200, 2450, 2650, 2780, 2850, 2890]
        streamz_throughput = [498, 995, 1485, 1975, 2480, 2960, 3420, 3850, 4200, 4450]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot throughput lines
        ax.plot(input_rates, faust_throughput, 'o-', label='Faust', 
                linewidth=2, markersize=8, color='#2E86AB')
        ax.plot(input_rates, streamz_throughput, 's-', label='Streamz',
                linewidth=2, markersize=8, color='#A23B72')
        
        # Ideal throughput line
        ax.plot([0, 5000], [0, 5000], '--', label='Ideal Throughput',
                linewidth=1.5, color='gray', alpha=0.7)
        
        ax.set_xlabel('Input Rate (events/second)', fontsize=12)
        ax.set_ylabel('Sustained Throughput (events/second)', fontsize=12)
        ax.set_xlim(0, 5500)
        ax.set_ylim(0, 5500)
        ax.legend(loc='lower right', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / 'figure1_throughput_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()
    
    def plot_efficiency_scaling(self):
        """Figure 2: Processing efficiency degradation under increasing load"""
        logger.info("Generating efficiency scaling figure...")
        
        input_rates = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
        
        # Calculate efficiency = (sustained_throughput / input_rate) * 100
        faust_efficiency = [97.0, 92.0, 92.0, 92.5, 88.0, 81.7, 75.7, 69.5, 63.3, 57.8]
        streamz_efficiency = [99.6, 99.5, 99.0, 98.8, 99.2, 98.7, 97.7, 96.3, 93.3, 89.0]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(input_rates, faust_efficiency, 'o-', label='Faust',
                linewidth=2, markersize=8, color='#2E86AB')
        ax.plot(input_rates, streamz_efficiency, 's-', label='Streamz',
                linewidth=2, markersize=8, color='#A23B72')
        
        ax.set_xlabel('Input Rate (events/second)', fontsize=12)
        ax.set_ylabel('Processing Efficiency (%)', fontsize=12)
        ax.set_xlim(0, 5500)
        ax.set_ylim(50, 102)
        ax.legend(loc='lower left', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Add reference lines
        ax.axhline(y=95, color='gray', linestyle=':', alpha=0.5, label='95% efficiency')
        ax.axhline(y=90, color='gray', linestyle=':', alpha=0.5, label='90% efficiency')
        
        plt.tight_layout()
        output_path = self.output_dir / 'figure2_efficiency_scaling.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()
    
    def plot_latency_distribution(self):
        """Latency distribution comparison"""
        logger.info("Generating latency distribution figure...")
        
        percentiles = ['P50', 'P75', 'P90', 'P95', 'P99']
        faust_latency = [45, 63, 78, 89, 156]
        streamz_latency = [12, 21, 34, 41, 89]
        
        x = np.arange(len(percentiles))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars1 = ax.bar(x - width/2, faust_latency, width, label='Faust', color='#2E86AB')
        bars2 = ax.bar(x + width/2, streamz_latency, width, label='Streamz', color='#A23B72')
        
        ax.set_xlabel('Latency Percentile', fontsize=12)
        ax.set_ylabel('Latency (milliseconds)', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(percentiles)
        ax.legend(fontsize=11)
        ax.grid(True, axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}ms',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        output_path = self.output_dir / 'figure3_latency_distribution.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()
    
    def plot_resource_comparison(self):
        """Resource utilization comparison"""
        logger.info("Generating resource comparison figure...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # CPU Usage
        engines = ['Faust', 'Streamz']
        cpu_mean = [24.8, 37.3]
        cpu_peak = [28.1, 47.2]
        
        x = np.arange(len(engines))
        width = 0.35
        
        ax1.bar(x - width/2, cpu_mean, width, label='Mean CPU', color='#2E86AB')
        ax1.bar(x + width/2, cpu_peak, width, label='Peak CPU', color='#A23B72')
        ax1.set_ylabel('CPU Usage (%)', fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(engines)
        ax1.legend(fontsize=10)
        ax1.set_title('CPU Utilization', fontsize=13)
        ax1.grid(True, axis='y', alpha=0.3)
        
        # Memory Usage
        memory = [83, 40]
        
        ax2.bar(engines, memory, color=['#2E86AB', '#A23B72'])
        ax2.set_ylabel('Memory Usage (MB)', fontsize=12)
        ax2.set_title('Steady-State Memory Consumption', fontsize=13)
        ax2.grid(True, axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(memory):
            ax2.text(i, v, f'{v}MB', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        output_path = self.output_dir / 'figure4_resource_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()
    
    def plot_pattern_detection_accuracy(self):
        """Pattern detection accuracy vs load"""
        logger.info("Generating pattern detection accuracy figure...")
        
        load_levels = [500, 1000, 1500, 2000, 2500, 3000]
        precision = [98.1, 97.8, 96.8, 96.2, 94.5, 92.5]
        recall = [97.9, 97.1, 96.2, 95.3, 93.8, 91.2]
        f1_score = [98.0, 97.4, 96.5, 95.7, 94.2, 91.8]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(load_levels, precision, 'o-', label='Precision', 
                linewidth=2, markersize=8)
        ax.plot(load_levels, recall, 's-', label='Recall',
                linewidth=2, markersize=8)
        ax.plot(load_levels, f1_score, '^-', label='F1-Score',
                linewidth=2, markersize=8)
        
        ax.set_xlabel('Load (events/second)', fontsize=12)
        ax.set_ylabel('Accuracy (%)', fontsize=12)
        ax.set_ylim(88, 100)
        ax.legend(loc='lower left', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=95, color='red', linestyle='--', alpha=0.5, 
                  label='95% threshold')
        
        plt.tight_layout()
        output_path = self.output_dir / 'figure5_pattern_accuracy.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
        plt.close()
    
    def generate_all_figures(self):
        """Generate all figures"""
        logger.info("Generating all figures...")
        
        self.plot_throughput_comparison()
        self.plot_efficiency_scaling()
        self.plot_latency_distribution()
        self.plot_resource_comparison()
        self.plot_pattern_detection_accuracy()
        
        logger.info(f"All figures saved to {self.output_dir}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate CEP benchmark figures')
    parser.add_argument('--output', type=str, default='results/figures',
                       help='Output directory for figures')
    parser.add_argument('--figure', type=str,
                       choices=['throughput', 'efficiency', 'latency', 'resources', 'patterns'],
                       help='Generate specific figure')
    parser.add_argument('--all-figures', action='store_true',
                       help='Generate all figures')
    
    args = parser.parse_args()
    
    viz = BenchmarkVisualizer(args.output)
    
    if args.all_figures or not args.figure:
        viz.generate_all_figures()
    else:
        if args.figure == 'throughput':
            viz.plot_throughput_comparison()
        elif args.figure == 'efficiency':
            viz.plot_efficiency_scaling()
        elif args.figure == 'latency':
            viz.plot_latency_distribution()
        elif args.figure == 'resources':
            viz.plot_resource_comparison()
        elif args.figure == 'patterns':
            viz.plot_pattern_detection_accuracy()


if __name__ == '__main__':
    main()
