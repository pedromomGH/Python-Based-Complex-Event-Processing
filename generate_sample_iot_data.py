"""
Generate sample IoT network intrusion dataset
This creates a small representative sample for testing and validation
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Number of sample events
N_EVENTS = 1000

# Generate timestamps
start_time = datetime(2024, 1, 1, 0, 0, 0)
timestamps = [start_time + timedelta(seconds=i*10 + np.random.randint(-5, 5)) 
              for i in range(N_EVENTS)]

# Generate device IDs
device_ids = [f"device_{i:03d}" for i in np.random.randint(1, 84, N_EVENTS)]

# Generate event types
event_types = np.random.choice(
    ['HTTP', 'DNS', 'TCP', 'UDP', 'ICMP', 'TLS'], 
    size=N_EVENTS,
    p=[0.35, 0.25, 0.20, 0.10, 0.05, 0.05]
)

# Generate network metrics
packet_sizes = np.random.lognormal(7.0, 1.5, N_EVENTS).astype(int)
packet_counts = np.random.poisson(50, N_EVENTS)
flow_duration = np.random.exponential(30, N_EVENTS)
bytes_sent = np.random.lognormal(10.0, 2.0, N_EVENTS).astype(int)
bytes_received = np.random.lognormal(10.5, 2.0, N_EVENTS).astype(int)

# Generate source/destination IPs
src_ips = [f"192.168.1.{np.random.randint(1, 255)}" for _ in range(N_EVENTS)]
dst_ips = [f"10.0.{np.random.randint(0, 255)}.{np.random.randint(1, 255)}" 
           for _ in range(N_EVENTS)]

# Generate ports
src_ports = np.random.randint(1024, 65535, N_EVENTS)
dst_ports = np.random.choice(
    [80, 443, 22, 25, 53, 3306, 8080] + list(range(1024, 65535, 100)),
    size=N_EVENTS
)

# Generate protocol flags
tcp_flags = np.random.choice(
    ['SYN', 'ACK', 'FIN', 'PSH', 'RST', 'SYN-ACK', 'PSH-ACK'],
    size=N_EVENTS
)

# Generate statistical features (simplified, 20 features instead of 115)
def generate_statistical_features(n):
    features = {}
    for i in range(1, 21):
        features[f'feature_{i}'] = np.random.randn(n)
    return pd.DataFrame(features)

stat_features = generate_statistical_features(N_EVENTS)

# Generate labels (15% anomalies)
is_anomaly = np.random.random(N_EVENTS) < 0.15
labels = np.where(is_anomaly, 1, 0)

# Generate anomaly scores (higher for actual anomalies)
anomaly_scores = np.where(
    is_anomaly,
    np.random.uniform(0.7, 1.0, N_EVENTS),
    np.random.uniform(0.0, 0.3, N_EVENTS)
)

# Attack types (only for anomalies)
attack_types = np.where(
    is_anomaly,
    np.random.choice(['Mirai', 'BASHLITE', 'Scan', 'DDoS', 'Overflow'], N_EVENTS),
    'Normal'
)

# Create DataFrame
df = pd.DataFrame({
    'timestamp': timestamps,
    'device_id': device_ids,
    'event_type': event_types,
    'src_ip': src_ips,
    'dst_ip': dst_ips,
    'src_port': src_ports,
    'dst_port': dst_ports,
    'protocol': event_types,
    'packet_size': packet_sizes,
    'packet_count': packet_counts,
    'flow_duration': flow_duration,
    'bytes_sent': bytes_sent,
    'bytes_received': bytes_received,
    'tcp_flags': tcp_flags,
    'label': labels,
    'anomaly_score': anomaly_scores,
    'attack_type': attack_types
})

# Add statistical features
df = pd.concat([df, stat_features], axis=1)

# Save to CSV
df.to_csv('sample_iot_data.csv', index=False)
print(f"Generated {N_EVENTS} IoT events")
print(f"Anomalies: {is_anomaly.sum()} ({100*is_anomaly.mean():.1f}%)")
print(f"Attack types distribution:")
print(df[df['label']==1]['attack_type'].value_counts())
print("\nSaved to: sample_iot_data.csv")
