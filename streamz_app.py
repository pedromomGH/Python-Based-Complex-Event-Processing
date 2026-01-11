"""
Streamz-based Complex Event Processing Engine
Implements lightweight stateless event processing for high throughput
"""
import json
import logging
import os
import time
from datetime import datetime
from collections import deque
from kafka import KafkaConsumer
from streamz import Stream
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil

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
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0]
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


class StreamzCEPEngine:
    """Streamz-based CEP engine optimized for throughput"""
    
    def __init__(self):
        self.kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.buffer_size = int(os.getenv('STREAMZ_BUFFER_SIZE', 100))
        self.poll_interval = int(os.getenv('STREAMZ_POLL_INTERVAL_MS', 100))
        self.fetch_max_bytes = int(os.getenv('STREAMZ_FETCH_MAX_BYTES', 1048576))
        
        # In-memory buffers for simple pattern detection
        self.recent_anomalies = deque(maxlen=self.buffer_size)
        self.recent_transactions = deque(maxlen=self.buffer_size)
        
        # Metrics tracking
        self.start_time = time.time()
        self.event_count = 0
        self.last_throughput_update = time.time()
        self.last_event_count = 0
        
        logger.info("Streamz CEP Engine initialized")
    
    def create_kafka_consumer(self, topic: str):
        """Create Kafka consumer"""
        return KafkaConsumer(
            topic,
            bootstrap_servers=self.kafka_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            max_poll_interval_ms=self.poll_interval,
            fetch_max_bytes=self.fetch_max_bytes,
            consumer_timeout_ms=1000  # Timeout for polling
        )
    
    def process_event(self, event: dict):
        """Process individual event"""
        start_time = time.time()
        
        try:
            # Extract event type
            event_type = event.get('event_type', 'unknown')
            
            # Basic transformations
            event['processed_at'] = datetime.now().isoformat()
            event['processing_timestamp'] = start_time
            
            # Simple threshold-based anomaly detection
            if event.get('anomaly_score', 0) > 0.8:
                self.recent_anomalies.append({
                    'entity_id': event['entity_id'],
                    'timestamp': event['timestamp'],
                    'score': event['anomaly_score']
                })
            
            # Track high-value transactions (for financial events)
            if 'amount' in event and event['amount'] > 5000:
                self.recent_transactions.append({
                    'entity_id': event['entity_id'],
                    'timestamp': event['timestamp'],
                    'amount': event['amount']
                })
            
            # Record metrics
            events_processed.labels(engine='streamz', event_type=event_type).inc()
            
            # Measure latency
            latency = time.time() - start_time
            processing_latency.labels(engine='streamz').observe(latency)
            
            # Update event count
            self.event_count += 1
            
            return event
            
        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
            return None
    
    def update_throughput(self):
        """Update throughput metric"""
        current_time = time.time()
        time_delta = current_time - self.last_throughput_update
        
        if time_delta >= 5.0:  # Update every 5 seconds
            event_delta = self.event_count - self.last_event_count
            throughput = event_delta / time_delta
            throughput_gauge.labels(engine='streamz').set(throughput)
            
            self.last_throughput_update = current_time
            self.last_event_count = self.event_count
            
            logger.info(f"Current throughput: {throughput:.2f} events/sec")
    
    def update_resource_metrics(self):
        """Update resource usage metrics"""
        try:
            process = psutil.Process()
            
            # Memory usage
            mem_info = process.memory_info()
            memory_usage.labels(engine='streamz').set(mem_info.rss)
            
            # CPU usage
            cpu_percent = process.cpu_percent(interval=None)
            cpu_usage.labels(engine='streamz').set(cpu_percent)
            
        except Exception as e:
            logger.warning(f"Error updating resource metrics: {e}")
    
    def run_iot_pipeline(self):
        """Run IoT event processing pipeline"""
        logger.info("Starting IoT processing pipeline")
        
        # Create Kafka consumer
        consumer = self.create_kafka_consumer('iot-events')
        
        # Create Streamz pipeline
        source = Stream()
        pipeline = (source
                   .map(self.process_event)
                   .filter(lambda x: x is not None)
                   .sink(lambda x: None))  # Sink to complete the pipeline
        
        # Process events
        try:
            for message in consumer:
                event = message.value
                source.emit(event)
                
                # Update metrics periodically
                if self.event_count % 100 == 0:
                    self.update_throughput()
                    self.update_resource_metrics()
                    
        except KeyboardInterrupt:
            logger.info("Shutting down IoT pipeline")
        finally:
            consumer.close()
    
    def run_financial_pipeline(self):
        """Run financial transaction processing pipeline"""
        logger.info("Starting financial processing pipeline")
        
        # Create Kafka consumer
        consumer = self.create_kafka_consumer('financial-events')
        
        # Create Streamz pipeline
        source = Stream()
        pipeline = (source
                   .map(self.process_event)
                   .filter(lambda x: x is not None)
                   .sink(lambda x: None))  # Sink to complete the pipeline
        
        # Process events
        try:
            for message in consumer:
                event = message.value
                source.emit(event)
                
                # Update metrics periodically
                if self.event_count % 100 == 0:
                    self.update_throughput()
                    self.update_resource_metrics()
                    
        except KeyboardInterrupt:
            logger.info("Shutting down financial pipeline")
        finally:
            consumer.close()
    
    def run(self, dataset_type='iot'):
        """Run the CEP engine"""
        logger.info(f"Starting Streamz CEP Engine for {dataset_type} dataset")
        
        # Start metrics server
        metrics_port = int(os.getenv('PROMETHEUS_PORT', 8002))
        start_http_server(metrics_port)
        logger.info(f"Prometheus metrics server started on port {metrics_port}")
        
        # Run appropriate pipeline
        if dataset_type == 'iot':
            self.run_iot_pipeline()
        elif dataset_type == 'financial':
            self.run_financial_pipeline()
        else:
            logger.error(f"Unknown dataset type: {dataset_type}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Streamz CEP Engine')
    parser.add_argument('--dataset', type=str, default='iot',
                       choices=['iot', 'financial'],
                       help='Dataset type to process')
    
    args = parser.parse_args()
    
    engine = StreamzCEPEngine()
    engine.run(args.dataset)


if __name__ == '__main__':
    main()
