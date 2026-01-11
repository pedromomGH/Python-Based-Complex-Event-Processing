# Dataset Documentation

## Overview

This directory contains sample datasets for testing the CEP benchmark. The full datasets should be downloaded separately as described in the main README.

## Sample Datasets

### IoT Network Intrusion Dataset (`sample_iot_data.csv`)

- **Source**: Simulated from IoT Network Intrusion Dataset (IEEE Dataport DOI: 10.21227/q70p-q449)
- **Size**: 1,000 events
- **Time Span**: Approx. 3 hours of simulated network traffic
- **Anomaly Rate**: ~15%
- **Features**: 37 fields including:
  - Network metrics (packet size, count, duration, bytes sent/received)
  - Connection info (source/destination IPs and ports)
  - Protocol information
  - Statistical features (20 derived features)
  - Ground truth labels and anomaly scores

**Attack Types Distribution**:
- Scan: ~26%
- DDoS: ~21%
- Overflow: ~20%
- Mirai: ~17%
- BASHLITE: ~16%

### Financial Transaction Dataset (`sample_financial_data.csv`)

- **Source**: Simulated PaySim-style mobile money transactions
- **Size**: 1,000 transactions
- **Time Span**: 30 simulated days
- **Fraud Rate**: ~2.1%
- **Features**: 15 fields including:
  - Transaction type (PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN)
  - Amount and balances (old/new for both source and destination)
  - Account identifiers
  - Fraud labels and scores
  - Derived features (balance changes, ratios)

**Transaction Type Distribution**:
- PAYMENT: ~31%
- TRANSFER: ~29%
- CASH_OUT: ~20%
- DEBIT: ~15%
- CASH_IN: ~5%

## Data Schema

### Standard Fields (Common to Both Datasets)

All events are normalized to include these standard fields:

```python
{
    "timestamp": str,        # ISO 8601 format
    "entity_id": str,        # Device ID or Account ID
    "event_type": str,       # Event classification
    "is_anomaly": int,       # Binary label (0 or 1)
    "anomaly_score": float   # Continuous score [0.0, 1.0]
}
```

### IoT-Specific Fields

```python
{
    "src_ip": str,
    "dst_ip": str,
    "src_port": int,
    "dst_port": int,
    "protocol": str,
    "packet_size": int,
    "packet_count": int,
    "flow_duration": float,
    "bytes_sent": int,
    "bytes_received": int,
    "tcp_flags": str,
    "attack_type": str,      # Only for anomalies
    "feature_1" through "feature_20": float
}
```

### Financial-Specific Fields

```python
{
    "type": str,             # Transaction type
    "amount": float,
    "nameOrig": str,         # Source account
    "oldbalanceOrg": float,
    "newbalanceOrig": float,
    "nameDest": str,         # Destination account
    "oldbalanceDest": float,
    "newbalanceDest": float,
    "step": int,             # Time step in simulation
    "isFraud": int,          # Binary fraud label
    "isFlaggedFraud": int,   # System-flagged fraud
    "fraud_score": float,
    "balance_change_src": float,
    "balance_change_dst": float,
    "is_merchant": int,
    "amount_ratio": float,
    "balance_ratio_src": float
}
```

## Preprocessing

Sample datasets are generated using:

```bash
python data/generate_iot_sample.py
python data/generate_financial_sample.py
```

For processing full datasets:

```bash
python preprocessing/data_preprocessor.py --dataset iot --input raw_iot.csv --output processed/iot.jsonl
python preprocessing/data_preprocessor.py --dataset financial --input raw_financial.csv --output processed/financial.jsonl
```

## Ground Truth Labels

### Anomaly/Fraud Labels

- **Original Labels**: Preserved from source datasets
- **Anomaly Scores**: Calculated using Isolation Forest (contamination=0.1)
- **Injected Patterns**: Some synthetic patterns added for pattern detection testing

### Pattern Labels

For pattern detection evaluation, events may have additional labels:

```python
{
    "pattern_id": str,         # Unique pattern identifier
    "pattern_type": str,       # e.g., "anomaly_burst", "fraud_sequence"
    "is_pattern_member": bool, # Part of a known pattern
    "pattern_timestamp": str   # When pattern was injected
}
```

## Data Quality

### Sample Data Characteristics

- **Realism**: Synthetic but based on real dataset distributions
- **Temporal Ordering**: Preserved, critical for CEP testing
- **Completeness**: No missing values in critical fields
- **Balance**: Natural imbalance (~15% anomalies, ~2% fraud)

### Known Limitations

1. **Sample Size**: Only 1,000 events each (full datasets have 500K+ events)
2. **Simplified Features**: Reduced from 115 to 37 features for IoT
3. **Synthetic**: Not actual captured traffic/transactions
4. **Single Day**: Limited temporal diversity

## Full Dataset Download

### IoT Network Intrusion Dataset

1. Visit: https://ieee-dataport.org/open-access/iot-network-intrusion-dataset
2. Download: `IoT_data.csv` (583,485 events, ~500MB)
3. Place in: `data/raw/iot_network_intrusion.csv`
4. Process: `python preprocessing/data_preprocessor.py --dataset iot --input data/raw/iot_network_intrusion.csv`

### PaySim Financial Dataset

1. Visit: https://www.kaggle.com/datasets/ealaxi/paysim1
2. Download: `PS_20174392719_1491204439457_log.csv` (6.3M transactions, ~500MB)
3. Place in: `data/raw/paysim_financial.csv`
4. Process: `python preprocessing/data_preprocessor.py --dataset financial --input data/raw/paysim_financial.csv`

## Citation

If you use these datasets, please cite:

**IoT Dataset**:
```
@data{iot-intrusion-2020,
  author = {Hussain, Fatima and Hassan, Syed Ali and Hussain, Rasheed and Hossain, Ekram},
  title = {IoT Network Intrusion Dataset},
  year = {2020},
  publisher = {IEEE Dataport},
  doi = {10.21227/q70p-q449}
}
```

**PaySim Dataset**:
```
@inproceedings{paysim-2016,
  author = {Lopez-Rojas, Edgar Alonso and Axelsson, Stefan},
  title = {PaySim: A Financial Mobile Money Simulator for Fraud Detection},
  booktitle = {28th European Modeling and Simulation Symposium},
  year = {2016}
}
```

## License

- **IoT Dataset**: CC BY 4.0
- **PaySim Dataset**: CC BY-SA 4.0
- **Sample Data**: MIT License (generated for this benchmark)

## Support

For questions about the data:
- See main README
- Open an issue on GitHub
- Contact: pedromom@estgv.ipv.pt
