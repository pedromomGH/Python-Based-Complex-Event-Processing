"""
Faust-based Complex Event Processing Engine
Implements stateful pattern detection for IoT and financial datasets
"""
import faust
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import os
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
events_processed = Counter(
    'cep_events_processed_total',
    'Total number of events processed',
    ['engine', 'event_type']
)

processing_latency = Histogram(
    'cep_processing_latency_seconds',
    'Event processing latency in seconds',
    ['engine'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

patterns_detected = Counter(
    'cep_patterns_detected_total',
    'Total number of patterns detected',
    ['engine', 'pattern_type']
)

throughput_gauge = Gauge(
    'cep_throughput_events_per_second',
    'Current event processing throughput',
    ['engine']
)

memory_usage = Gauge(
    'cep_memory_bytes',
    'Memory usage in bytes',
    ['engine']
)

cpu_usage = Gauge(
    'cep_cpu_usage_percent',
    'CPU usage percentage',
    ['engine']
)

# Pattern detection results
pattern_precision = Gauge(
    'cep_pattern_precision',
    'Pattern detection precision',
    ['engine', 'pattern_type']
)

pattern_recall = Gauge(
    'cep_pattern_recall',
    'Pattern detection recall',
    ['engine', 'pattern_type']
)


# Faust app configuration
app = faust.App(
    'cep-faust',
    broker=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka://localhost:9092'),
    store='rocksdb://',
    web_port=int(os.getenv('FAUST_WEB_PORT', 6066)),
    web_host=os.getenv('FAUST_WEB_HOST', '0.0.0.0'),
    stream_buffer_maxsize=int(os.getenv('FAUST_STREAM_BUFFER_MAXSIZE', 4096)),
    broker_commit_interval=float(os.getenv('FAUST_BROKER_COMMIT_INTERVAL', 1.0)),
)


# Record schemas
class Event(faust.Record, serializer='json'):
    """Base event record"""
    timestamp: str
    entity_id: str
    event_type: str
    is_anomaly: int
    anomaly_score: float
    processing_start: float = None  # For latency measurement


class IoTEvent(Event):
    """IoT-specific event"""
    src_ip: str = None
    dst_ip: str = None
    src_port: int = None
    dst_port: int = None
    packet_size: int = None
    packet_count: int = None
    flow_duration: float = None
    bytes_sent: int = None
    bytes_received: int = None


class FinancialEvent(Event):
    """Financial transaction event"""
    amount: float = None
    nameOrig: str = None
    oldbalanceOrg: float = None
    newbalanceOrig: float = None
    nameDest: str = None
    oldbalanceDest: float = None
    newbalanceDest: float = None
    step: int = None


class PatternDetection(faust.Record, serializer='json'):
    """Pattern detection result"""
    pattern_type: str
    entity_id: str
    timestamp: str
    events: List[Dict[str, Any]]
    confidence: float
    description: str


# Topics
iot_events_topic = app.topic('iot-events', value_type=IoTEvent)
financial_events_topic = app.topic('financial-events', value_type=FinancialEvent)
patterns_topic = app.topic('detected-patterns', value_type=PatternDetection)

# Tables for stateful pattern detection
anomaly_windows = app.Table('anomaly_windows', default=list)
transaction_windows = app.Table('transaction_windows', default=list)
fraud_sequences = app.Table('fraud_sequences', default=list)

# Pattern detection statistics
pattern_stats = app.Table('pattern_stats', default=dict)


@app.agent(iot_events_topic)
async def process_iot_events(events):
    """Process IoT events and detect anomaly patterns"""
    logger.info("IoT event processor started")
    
    async for event in events.group_by(lambda e: e.entity_id):
        start_time = time.time()
        
        try:
            # Record metrics
            events_processed.labels(engine='faust', event_type='iot').inc()
            
            # Detect anomaly burst pattern
            # Pattern: 5+ anomalies with score > 0.8 within 60 seconds
            await detect_anomaly_burst(event)
            
            # Measure latency
            latency = time.time() - start_time
            processing_latency.labels(engine='faust').observe(latency)
            
        except Exception as e:
            logger.error(f"Error processing IoT event: {e}", exc_info=True)


@app.agent(financial_events_topic)
async def process_financial_events(events):
    """Process financial events and detect fraud patterns"""
    logger.info("Financial event processor started")
    
    async for event in events.group_by(lambda e: e.entity_id):
        start_time = time.time()
        
        try:
            # Record metrics
            events_processed.labels(engine='faust', event_type='financial').inc()
            
            # Detect high-value transaction burst
            # Pattern: 3+ transactions > $5000 within 30 seconds
            await detect_high_value_burst(event)
            
            # Detect fraud sequence
            # Pattern: Multiple transactions with fraud score > 0.9
            await detect_fraud_sequence(event)
            
            # Measure latency
            latency = time.time() - start_time
            processing_latency.labels(engine='faust').observe(latency)
            
        except Exception as e:
            logger.error(f"Error processing financial event: {e}", exc_info=True)


async def detect_anomaly_burst(event: IoTEvent):
    """Detect burst of anomalies from same device"""
    entity_id = event.entity_id
    current_time = datetime.fromisoformat(event.timestamp)
    
    # Get current window
    window = anomaly_windows[entity_id]
    
    # Add current event if it's an anomaly with high score
    if event.anomaly_score > 0.8:
        window.append({
            'timestamp': event.timestamp,
            'score': event.anomaly_score,
            'event_type': event.event_type
        })
    
    # Remove events outside 60-second window
    cutoff_time = current_time - timedelta(seconds=60)
    window = [e for e in window 
              if datetime.fromisoformat(e['timestamp']) > cutoff_time]
    
    # Update table
    anomaly_windows[entity_id] = window
    
    # Check if pattern detected
    if len(window) >= 5:
        pattern = PatternDetection(
            pattern_type='anomaly_burst',
            entity_id=entity_id,
            timestamp=current_time.isoformat(),
            events=window,
            confidence=sum(e['score'] for e in window) / len(window),
            description=f"Detected {len(window)} high-score anomalies in 60s window"
        )
        
        await patterns_topic.send(value=pattern)
        patterns_detected.labels(engine='faust', pattern_type='anomaly_burst').inc()
        
        # Update statistics
        stats = pattern_stats.get('anomaly_burst', {
            'total_detected': 0,
            'true_positives': 0,
            'false_positives': 0
        })
        stats['total_detected'] += 1
        
        # Ground truth: check if original events were labeled anomalies
        if event.is_anomaly == 1:
            stats['true_positives'] += 1
        else:
            stats['false_positives'] += 1
        
        pattern_stats['anomaly_burst'] = stats
        
        # Update metrics
        if stats['total_detected'] > 0:
            precision = stats['true_positives'] / stats['total_detected']
            pattern_precision.labels(
                engine='faust',
                pattern_type='anomaly_burst'
            ).set(precision)
        
        logger.info(f"Anomaly burst detected for {entity_id}: {len(window)} events")


async def detect_high_value_burst(event: FinancialEvent):
    """Detect burst of high-value transactions"""
    entity_id = event.entity_id
    current_time = datetime.fromisoformat(event.timestamp)
    
    # Get current window
    window = transaction_windows[entity_id]
    
    # Add current event if high value (> $5000)
    if event.amount and event.amount > 5000:
        window.append({
            'timestamp': event.timestamp,
            'amount': event.amount,
            'type': event.event_type,
            'destination': event.nameDest
        })
    
    # Remove events outside 30-second window
    cutoff_time = current_time - timedelta(seconds=30)
    window = [e for e in window 
              if datetime.fromisoformat(e['timestamp']) > cutoff_time]
    
    # Update table
    transaction_windows[entity_id] = window
    
    # Check if pattern detected
    if len(window) >= 3:
        total_amount = sum(e['amount'] for e in window)
        
        pattern = PatternDetection(
            pattern_type='high_value_burst',
            entity_id=entity_id,
            timestamp=current_time.isoformat(),
            events=window,
            confidence=min(1.0, len(window) / 5),  # Confidence based on count
            description=f"Detected {len(window)} high-value transactions totaling ${total_amount:,.2f}"
        )
        
        await patterns_topic.send(value=pattern)
        patterns_detected.labels(engine='faust', pattern_type='high_value_burst').inc()
        
        # Update statistics
        stats = pattern_stats.get('high_value_burst', {
            'total_detected': 0,
            'true_positives': 0,
            'false_positives': 0
        })
        stats['total_detected'] += 1
        
        if event.is_anomaly == 1:
            stats['true_positives'] += 1
        else:
            stats['false_positives'] += 1
        
        pattern_stats['high_value_burst'] = stats
        
        if stats['total_detected'] > 0:
            precision = stats['true_positives'] / stats['total_detected']
            pattern_precision.labels(
                engine='faust',
                pattern_type='high_value_burst'
            ).set(precision)
        
        logger.info(f"High-value burst detected for {entity_id}: {len(window)} transactions")


async def detect_fraud_sequence(event: FinancialEvent):
    """Detect sequence of fraudulent transactions"""
    entity_id = event.entity_id
    current_time = datetime.fromisoformat(event.timestamp)
    
    # Get current sequence
    sequence = fraud_sequences[entity_id]
    
    # Add current event if high fraud score
    if event.anomaly_score > 0.9:
        sequence.append({
            'timestamp': event.timestamp,
            'fraud_score': event.anomaly_score,
            'amount': event.amount,
            'type': event.event_type
        })
    
    # Keep last 10 events
    if len(sequence) > 10:
        sequence = sequence[-10:]
    
    # Update table
    fraud_sequences[entity_id] = sequence
    
    # Check if pattern detected (2+ in sequence)
    if len(sequence) >= 2:
        avg_score = sum(e['fraud_score'] for e in sequence) / len(sequence)
        
        pattern = PatternDetection(
            pattern_type='fraud_sequence',
            entity_id=entity_id,
            timestamp=current_time.isoformat(),
            events=sequence,
            confidence=avg_score,
            description=f"Detected fraud sequence: {len(sequence)} transactions with avg score {avg_score:.2f}"
        )
        
        await patterns_topic.send(value=pattern)
        patterns_detected.labels(engine='faust', pattern_type='fraud_sequence').inc()
        
        # Update statistics
        stats = pattern_stats.get('fraud_sequence', {
            'total_detected': 0,
            'true_positives': 0,
            'false_positives': 0
        })
        stats['total_detected'] += 1
        
        if event.is_anomaly == 1:
            stats['true_positives'] += 1
        else:
            stats['false_positives'] += 1
        
        pattern_stats['fraud_sequence'] = stats
        
        if stats['total_detected'] > 0:
            precision = stats['true_positives'] / stats['total_detected']
            pattern_precision.labels(
                engine='faust',
                pattern_type='fraud_sequence'
            ).set(precision)


@app.timer(interval=5.0)
async def update_throughput_metrics():
    """Update throughput metrics periodically"""
    try:
        # Get event count in last 5 seconds
        current_count = events_processed._metrics.get(
            ('faust', 'iot'),
            events_processed._metrics.get(('faust', 'financial'), None)
        )
        
        if hasattr(update_throughput_metrics, 'last_count'):
            events_delta = current_count._value.get() - update_throughput_metrics.last_count
            throughput = events_delta / 5.0  # Events per second
            throughput_gauge.labels(engine='faust').set(throughput)
        
        if current_count:
            update_throughput_metrics.last_count = current_count._value.get()
            
    except Exception as e:
        logger.warning(f"Error updating throughput metrics: {e}")


@app.timer(interval=10.0)
async def update_resource_metrics():
    """Update resource usage metrics"""
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Memory usage
        mem_info = process.memory_info()
        memory_usage.labels(engine='faust').set(mem_info.rss)
        
        # CPU usage
        cpu_percent = process.cpu_percent(interval=1)
        cpu_usage.labels(engine='faust').set(cpu_percent)
        
    except Exception as e:
        logger.warning(f"Error updating resource metrics: {e}")


@app.command()
async def start_metrics_server():
    """Start Prometheus metrics HTTP server"""
    port = int(os.getenv('PROMETHEUS_PORT', 8001))
    start_http_server(port)
    logger.info(f"Prometheus metrics server started on port {port}")


if __name__ == '__main__':
    # Start metrics server
    import asyncio
    metrics_port = int(os.getenv('PROMETHEUS_PORT', 8001))
    start_http_server(metrics_port)
    logger.info(f"Prometheus metrics server started on port {metrics_port}")
    
    # Run Faust app
    app.main()
