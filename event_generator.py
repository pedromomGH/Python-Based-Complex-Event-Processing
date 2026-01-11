"""
Event Generator for CEP Benchmark
Generates realistic event streams from preprocessed data
"""
import argparse
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Iterator
from kafka import KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventGenerator:
    """Generates event streams for CEP benchmarking"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='snappy',
            batch_size=16384,
            linger_ms=10,
            buffer_memory=33554432
        )
        logger.info(f"Event generator initialized with broker: {bootstrap_servers}")
    
    def load_dataset(self, filepath: str) -> Iterator[dict]:
        """Load events from JSONL file"""
        logger.info(f"Loading dataset from {filepath}")
        
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Dataset not found: {filepath}")
        
        event_count = 0
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    event_count += 1
                    yield event
        
        logger.info(f"Loaded {event_count} events from dataset")
    
    def generate_stream(
        self,
        dataset_path: str,
        topic: str,
        rate: int,
        duration_seconds: int = None,
        repeat: bool = True
    ):
        """Generate event stream at specified rate"""
        logger.info(f"Starting event generation:")
        logger.info(f"  Topic: {topic}")
        logger.info(f"  Rate: {rate} events/second")
        logger.info(f"  Duration: {duration_seconds}s" if duration_seconds else "  Duration: continuous")
        logger.info(f"  Repeat: {repeat}")
        
        start_time = time.time()
        events_sent = 0
        target_interval = 1.0 / rate  # Time between events
        
        events = list(self.load_dataset(dataset_path))
        event_idx = 0
        
        try:
            while True:
                # Check duration limit
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    logger.info(f"Duration limit reached ({duration_seconds}s)")
                    break
                
                # Get next event
                if event_idx >= len(events):
                    if not repeat:
                        logger.info("Dataset exhausted, stopping")
                        break
                    event_idx = 0  # Restart from beginning
                
                event = events[event_idx]
                event_idx += 1
                
                # Send event to Kafka
                try:
                    self.producer.send(topic, value=event)
                    events_sent += 1
                    
                    # Rate limiting
                    expected_time = start_time + (events_sent * target_interval)
                    current_time = time.time()
                    sleep_time = expected_time - current_time
                    
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                    # Progress logging
                    if events_sent % 1000 == 0:
                        elapsed = time.time() - start_time
                        actual_rate = events_sent / elapsed if elapsed > 0 else 0
                        logger.info(f"Sent {events_sent} events, actual rate: {actual_rate:.2f} eps")
                    
                except KafkaError as e:
                    logger.error(f"Error sending event: {e}")
                    continue
                
        except KeyboardInterrupt:
            logger.info("Generator stopped by user")
        finally:
            # Flush remaining messages
            self.producer.flush()
            
            # Final statistics
            elapsed = time.time() - start_time
            actual_rate = events_sent / elapsed if elapsed > 0 else 0
            
            logger.info("=" * 60)
            logger.info("Event Generation Summary:")
            logger.info(f"  Total events sent: {events_sent}")
            logger.info(f"  Elapsed time: {elapsed:.2f}s")
            logger.info(f"  Target rate: {rate} eps")
            logger.info(f"  Actual rate: {actual_rate:.2f} eps")
            logger.info(f"  Efficiency: {(actual_rate/rate)*100:.1f}%")
            logger.info("=" * 60)
            
            self.producer.close()
    
    def generate_burst_pattern(
        self,
        dataset_path: str,
        topic: str,
        base_rate: int,
        burst_rate: int,
        burst_duration: int = 60,
        burst_interval: int = 300
    ):
        """Generate bursty traffic pattern"""
        logger.info("Starting burst pattern generation")
        logger.info(f"  Base rate: {base_rate} eps")
        logger.info(f"  Burst rate: {burst_rate} eps")
        logger.info(f"  Burst duration: {burst_duration}s")
        logger.info(f"  Burst interval: {burst_interval}s")
        
        start_time = time.time()
        events_sent = 0
        
        events = list(self.load_dataset(dataset_path))
        event_idx = 0
        
        try:
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Determine if in burst period
                cycle_position = elapsed % burst_interval
                in_burst = cycle_position < burst_duration
                current_rate = burst_rate if in_burst else base_rate
                
                # Get next event
                if event_idx >= len(events):
                    event_idx = 0
                
                event = events[event_idx]
                event_idx += 1
                
                # Send event
                try:
                    self.producer.send(topic, value=event)
                    events_sent += 1
                    
                    # Rate limiting
                    target_interval = 1.0 / current_rate
                    time.sleep(target_interval)
                    
                    # Status logging
                    if events_sent % 1000 == 0:
                        status = "BURST" if in_burst else "BASE"
                        logger.info(f"[{status}] Sent {events_sent} events at {current_rate} eps")
                    
                except KafkaError as e:
                    logger.error(f"Error sending event: {e}")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Burst generator stopped by user")
        finally:
            self.producer.flush()
            self.producer.close()


def main():
    parser = argparse.ArgumentParser(description='Event Generator for CEP Benchmark')
    parser.add_argument('--dataset', type=str, required=True,
                       choices=['iot', 'financial'],
                       help='Dataset type')
    parser.add_argument('--rate', type=int, required=True,
                       help='Event generation rate (events/second)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Generation duration in seconds (default: continuous)')
    parser.add_argument('--topic', type=str, default=None,
                       help='Kafka topic (default: {dataset}-events)')
    parser.add_argument('--broker', type=str,
                       default=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
                       help='Kafka bootstrap servers')
    parser.add_argument('--data-path', type=str, default='/data/processed',
                       help='Path to processed data directory')
    parser.add_argument('--burst', action='store_true',
                       help='Enable burst pattern generation')
    parser.add_argument('--burst-rate', type=int, default=None,
                       help='Burst rate (for burst mode)')
    
    args = parser.parse_args()
    
    # Determine topic
    topic = args.topic or f"{args.dataset}-events"
    
    # Determine dataset path
    dataset_file = f"sample_{args.dataset}.jsonl"
    dataset_path = Path(args.data_path) / dataset_file
    
    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        logger.info("Please run preprocessing first:")
        logger.info("  python preprocessing/data_preprocessor.py --sample")
        return
    
    # Create generator
    generator = EventGenerator(args.broker)
    
    # Generate events
    if args.burst and args.burst_rate:
        generator.generate_burst_pattern(
            str(dataset_path),
            topic,
            base_rate=args.rate,
            burst_rate=args.burst_rate
        )
    else:
        generator.generate_stream(
            str(dataset_path),
            topic,
            args.rate,
            args.duration
        )


if __name__ == '__main__':
    main()
