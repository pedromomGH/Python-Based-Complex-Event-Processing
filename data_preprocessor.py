"""
Data Preprocessor for CEP Benchmark
Standardizes datasets and prepares them for streaming
"""
import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import IsolationForest
from typing import Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocesses and standardizes datasets for CEP benchmarking"""
    
    def __init__(self, dataset_type: str):
        self.dataset_type = dataset_type
        self.isolation_forest = None
        
    def load_data(self, input_path: str) -> pd.DataFrame:
        """Load raw data from CSV"""
        logger.info(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} records")
        return df
    
    def normalize_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize timestamps while preserving ordering"""
        logger.info("Normalizing timestamps")
        
        if 'timestamp' in df.columns:
            # Already has timestamp column
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        else:
            # Generate timestamps based on ordering
            base_time = datetime(2024, 1, 1, 0, 0, 0)
            df['timestamp'] = pd.date_range(
                start=base_time,
                periods=len(df),
                freq='1S'  # 1 second intervals
            )
        
        # Sort by timestamp to ensure ordering
        df = df.sort_values('timestamp').reset_index(drop=True)
        return df
    
    def standardize_schema_iot(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize IoT dataset schema"""
        logger.info("Standardizing IoT schema")
        
        # Required fields for standardized schema
        standardized = pd.DataFrame({
            'timestamp': df['timestamp'],
            'entity_id': df['device_id'],
            'event_type': df['event_type'],
            'is_anomaly': df.get('label', 0),
            'anomaly_score': df.get('anomaly_score', 0.0)
        })
        
        # Extended schema with domain-specific fields
        extended_fields = [
            'src_ip', 'dst_ip', 'src_port', 'dst_port',
            'packet_size', 'packet_count', 'flow_duration',
            'bytes_sent', 'bytes_received'
        ]
        
        for field in extended_fields:
            if field in df.columns:
                standardized[field] = df[field]
        
        # Add statistical features
        feature_cols = [col for col in df.columns if col.startswith('feature_')]
        for col in feature_cols:
            standardized[col] = df[col]
        
        return standardized
    
    def standardize_schema_financial(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize financial dataset schema"""
        logger.info("Standardizing financial schema")
        
        # Required fields for standardized schema
        standardized = pd.DataFrame({
            'timestamp': df['timestamp'],
            'entity_id': df['nameOrig'],  # Source account
            'event_type': df['type'],
            'is_anomaly': df.get('isFraud', 0),
            'anomaly_score': df.get('fraud_score', 0.0)
        })
        
        # Extended schema with domain-specific fields
        extended_fields = [
            'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig',
            'nameDest', 'oldbalanceDest', 'newbalanceDest', 'step'
        ]
        
        for field in extended_fields:
            if field in df.columns:
                standardized[field] = df[field]
        
        # Add derived features if they exist
        derived_fields = [
            'balance_change_src', 'balance_change_dst',
            'amount_ratio', 'balance_ratio_src', 'is_merchant'
        ]
        
        for field in derived_fields:
            if field in df.columns:
                standardized[field] = df[field]
        
        return standardized
    
    def calculate_anomaly_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate anomaly scores using Isolation Forest if not present"""
        if 'anomaly_score' in df.columns and df['anomaly_score'].notna().all():
            logger.info("Anomaly scores already present")
            return df
        
        logger.info("Calculating anomaly scores using Isolation Forest")
        
        # Select numerical features for anomaly detection
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        exclude_cols = ['timestamp', 'is_anomaly', 'anomaly_score']
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if not feature_cols:
            logger.warning("No numerical features found for anomaly detection")
            df['anomaly_score'] = df.get('is_anomaly', 0).astype(float)
            return df
        
        # Prepare features
        X = df[feature_cols].fillna(0)
        
        # Train Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # Get anomaly scores (transform to 0-1 range)
        predictions = self.isolation_forest.fit_predict(X)
        scores = self.isolation_forest.score_samples(X)
        
        # Normalize scores to 0-1 range (higher = more anomalous)
        scores_normalized = 1 - (scores - scores.min()) / (scores.max() - scores.min())
        
        df['anomaly_score'] = scores_normalized
        
        logger.info(f"Anomaly score statistics: mean={scores_normalized.mean():.3f}, "
                   f"std={scores_normalized.std():.3f}")
        
        return df
    
    def convert_to_json_streaming(self, df: pd.DataFrame, output_path: str):
        """Convert to JSON Lines format for streaming"""
        logger.info(f"Converting to JSON streaming format: {output_path}")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for idx, row in df.iterrows():
                # Convert timestamp to ISO format
                row_dict = row.to_dict()
                row_dict['timestamp'] = row['timestamp'].isoformat()
                
                # Convert NaN to None
                row_dict = {k: (None if pd.isna(v) else v) 
                           for k, v in row_dict.items()}
                
                f.write(json.dumps(row_dict) + '\n')
        
        logger.info(f"Wrote {len(df)} events to {output_path}")
    
    def process(self, input_path: str, output_path: str):
        """Main processing pipeline"""
        logger.info(f"Processing {self.dataset_type} dataset")
        
        # Load data
        df = self.load_data(input_path)
        
        # Normalize timestamps
        df = self.normalize_timestamps(df)
        
        # Standardize schema based on dataset type
        if self.dataset_type == 'iot':
            df = self.standardize_schema_iot(df)
        elif self.dataset_type == 'financial':
            df = self.standardize_schema_financial(df)
        else:
            raise ValueError(f"Unknown dataset type: {self.dataset_type}")
        
        # Calculate anomaly scores
        df = self.calculate_anomaly_scores(df)
        
        # Convert to JSON streaming format
        self.convert_to_json_streaming(df, output_path)
        
        # Save metadata
        metadata = {
            'dataset_type': self.dataset_type,
            'num_events': len(df),
            'time_span_seconds': (df['timestamp'].max() - df['timestamp'].min()).total_seconds(),
            'anomaly_rate': df['is_anomaly'].mean(),
            'avg_anomaly_score': df['anomaly_score'].mean(),
            'event_types': df['event_type'].value_counts().to_dict(),
            'processed_at': datetime.now().isoformat()
        }
        
        metadata_path = output_path.replace('.jsonl', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata to {metadata_path}")
        logger.info("Processing complete")
        
        return df, metadata


def main():
    parser = argparse.ArgumentParser(description='Preprocess datasets for CEP benchmarking')
    parser.add_argument('--dataset', type=str, choices=['iot', 'financial'],
                       help='Dataset type to process')
    parser.add_argument('--input', type=str,
                       help='Input CSV file path')
    parser.add_argument('--output', type=str,
                       help='Output JSONL file path')
    parser.add_argument('--sample', action='store_true',
                       help='Process sample datasets')
    
    args = parser.parse_args()
    
    if args.sample:
        # Process sample datasets
        logger.info("Processing sample datasets")
        
        # IoT sample
        preprocessor = DataPreprocessor('iot')
        preprocessor.process(
            'data/sample_iot_data.csv',
            'data/processed/sample_iot.jsonl'
        )
        
        # Financial sample
        preprocessor = DataPreprocessor('financial')
        preprocessor.process(
            'data/sample_financial_data.csv',
            'data/processed/sample_financial.jsonl'
        )
    else:
        if not all([args.dataset, args.input, args.output]):
            parser.error("--dataset, --input, and --output are required unless using --sample")
        
        preprocessor = DataPreprocessor(args.dataset)
        preprocessor.process(args.input, args.output)


if __name__ == '__main__':
    main()
