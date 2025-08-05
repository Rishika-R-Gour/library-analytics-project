#!/usr/bin/env python3
"""
Pipeline Scheduler and Orchestrator
Handles automated execution and scheduling of ETL pipelines
"""

import os
import sys
import json
import logging
import schedule
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from dataclasses import dataclass
from enum import Enum
import subprocess
import psutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.etl_framework import ETLPipeline, ETLPipelineError
from pipelines.extractors.data_extractors import *
from pipelines.transformers.data_transformers import *
from pipelines.loaders.data_loaders import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"

@dataclass
class ScheduledPipeline:
    """Represents a scheduled pipeline"""
    name: str
    pipeline_config: Dict[str, Any]
    schedule_config: Dict[str, Any]
    status: PipelineStatus = PipelineStatus.SCHEDULED
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    enabled: bool = True

class PipelineScheduler:
    """Manages scheduled pipeline execution"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "schedulers/pipeline_schedules.json"
        self.scheduled_pipelines: Dict[str, ScheduledPipeline] = {}
        self.running_pipelines: Dict[str, Dict[str, Any]] = {}
        self.scheduler_thread: Optional[threading.Thread] = None
        self.stop_scheduler = False
        self.metrics_db_path = "monitoring/scheduler_metrics.db"
        
        # Initialize metrics database
        self._init_metrics_db()
        
        # Load pipeline configurations
        self._load_pipeline_configs()
    
    def _init_metrics_db(self):
        """Initialize scheduler metrics database"""
        try:
            os.makedirs(os.path.dirname(self.metrics_db_path), exist_ok=True)
            conn = sqlite3.connect(self.metrics_db_path)
            
            # Create tables for tracking pipeline executions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_name TEXT NOT NULL,
                    execution_id TEXT NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT,
                    duration_seconds REAL,
                    records_processed INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_name TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metric_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduler_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    pipeline_name TEXT,
                    message TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics database: {e}")
    
    def _load_pipeline_configs(self):
        """Load pipeline configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    configs = json.load(f)
                
                for name, config in configs.items():
                    scheduled_pipeline = ScheduledPipeline(
                        name=name,
                        pipeline_config=config['pipeline'],
                        schedule_config=config['schedule'],
                        enabled=config.get('enabled', True)
                    )
                    self.scheduled_pipelines[name] = scheduled_pipeline
                
                logger.info(f"Loaded {len(self.scheduled_pipelines)} pipeline configurations")
            else:
                logger.info(f"No configuration file found at {self.config_file}")
                
        except Exception as e:
            logger.error(f"Failed to load pipeline configurations: {e}")
    
    def add_scheduled_pipeline(self, name: str, pipeline_config: Dict[str, Any], 
                             schedule_config: Dict[str, Any], enabled: bool = True):
        """Add a new scheduled pipeline"""
        scheduled_pipeline = ScheduledPipeline(
            name=name,
            pipeline_config=pipeline_config,
            schedule_config=schedule_config,
            enabled=enabled
        )
        
        self.scheduled_pipelines[name] = scheduled_pipeline
        self._save_pipeline_configs()
        
        # Schedule the pipeline
        self._schedule_pipeline(scheduled_pipeline)
        
        logger.info(f"Added scheduled pipeline: {name}")
    
    def _schedule_pipeline(self, scheduled_pipeline: ScheduledPipeline):
        """Schedule a pipeline based on its configuration"""
        if not scheduled_pipeline.enabled:
            return
        
        schedule_config = scheduled_pipeline.schedule_config
        schedule_type = schedule_config.get('type', 'interval')
        
        if schedule_type == 'interval':
            # Schedule at regular intervals
            interval = schedule_config.get('interval', 60)  # minutes
            schedule.every(interval).minutes.do(
                self._execute_pipeline_wrapper,
                scheduled_pipeline.name
            ).tag(scheduled_pipeline.name)
            
        elif schedule_type == 'daily':
            # Schedule daily at specific time
            time_str = schedule_config.get('time', '02:00')
            schedule.every().day.at(time_str).do(
                self._execute_pipeline_wrapper,
                scheduled_pipeline.name
            ).tag(scheduled_pipeline.name)
            
        elif schedule_type == 'weekly':
            # Schedule weekly on specific day
            day = schedule_config.get('day', 'monday')
            time_str = schedule_config.get('time', '02:00')
            getattr(schedule.every(), day).at(time_str).do(
                self._execute_pipeline_wrapper,
                scheduled_pipeline.name
            ).tag(scheduled_pipeline.name)
            
        elif schedule_type == 'cron':
            # For more complex scheduling (would need additional library)
            logger.warning(f"Cron scheduling not implemented for {scheduled_pipeline.name}")
    
    def _execute_pipeline_wrapper(self, pipeline_name: str):
        """Wrapper for pipeline execution with error handling"""
        try:
            self.execute_pipeline(pipeline_name)
        except Exception as e:
            logger.error(f"Failed to execute scheduled pipeline {pipeline_name}: {e}")
            self._log_scheduler_event("execution_error", pipeline_name, str(e))
    
    def execute_pipeline(self, pipeline_name: str, manual: bool = False) -> Dict[str, Any]:
        """Execute a specific pipeline"""
        if pipeline_name not in self.scheduled_pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_name}")
        
        scheduled_pipeline = self.scheduled_pipelines[pipeline_name]
        
        if not scheduled_pipeline.enabled and not manual:
            logger.warning(f"Pipeline {pipeline_name} is disabled")
            return {"status": "disabled"}
        
        if pipeline_name in self.running_pipelines:
            logger.warning(f"Pipeline {pipeline_name} is already running")
            return {"status": "already_running"}
        
        # Update status
        scheduled_pipeline.status = PipelineStatus.RUNNING
        scheduled_pipeline.last_run = datetime.now()
        scheduled_pipeline.run_count += 1
        
        # Create and execute pipeline
        try:
            pipeline = self._create_pipeline(scheduled_pipeline)
            
            # Track running pipeline
            execution_info = {
                'pipeline': pipeline,
                'start_time': datetime.now(),
                'scheduled_pipeline': scheduled_pipeline
            }
            self.running_pipelines[pipeline_name] = execution_info
            
            # Execute pipeline
            results = pipeline.execute()
            
            # Update metrics
            self._update_pipeline_metrics(scheduled_pipeline, results)
            
            # Update status
            if results['status'] == 'completed':
                scheduled_pipeline.status = PipelineStatus.COMPLETED
                scheduled_pipeline.success_count += 1
            else:
                scheduled_pipeline.status = PipelineStatus.FAILED
                scheduled_pipeline.failure_count += 1
            
            logger.info(f"Pipeline {pipeline_name} completed with status: {results['status']}")
            
            return results
            
        except Exception as e:
            scheduled_pipeline.status = PipelineStatus.FAILED
            scheduled_pipeline.failure_count += 1
            logger.error(f"Pipeline {pipeline_name} failed: {e}")
            
            self._log_scheduler_event("execution_error", pipeline_name, str(e))
            
            return {"status": "failed", "error": str(e)}
            
        finally:
            # Remove from running pipelines
            if pipeline_name in self.running_pipelines:
                del self.running_pipelines[pipeline_name]
    
    def _create_pipeline(self, scheduled_pipeline: ScheduledPipeline) -> ETLPipeline:
        """Create ETL pipeline from configuration"""
        config = scheduled_pipeline.pipeline_config
        pipeline = ETLPipeline(scheduled_pipeline.name, config.get('config', {}))
        
        # Add extractors
        for extractor_config in config.get('extractors', []):
            extractor = self._create_component('extractor', extractor_config)
            pipeline.add_component(extractor)
        
        # Add transformers
        for transformer_config in config.get('transformers', []):
            transformer = self._create_component('transformer', transformer_config)
            pipeline.add_component(transformer)
        
        # Add loaders
        for loader_config in config.get('loaders', []):
            loader = self._create_component('loader', loader_config)
            pipeline.add_component(loader)
        
        return pipeline
    
    def _create_component(self, component_type: str, config: Dict[str, Any]):
        """Create ETL component from configuration"""
        component_class = config['class']
        component_name = config['name']
        component_params = config.get('params', {})
        component_config = config.get('config', {})
        
        # Get component class
        if component_type == 'extractor':
            if component_class == 'CSVExtractor':
                return CSVExtractor(component_name, **component_params, config=component_config)
            elif component_class == 'DatabaseExtractor':
                return DatabaseExtractor(component_name, **component_params, config=component_config)
            elif component_class == 'LibraryDataExtractor':
                return LibraryDataExtractor(component_name, **component_params, config=component_config)
            # Add more extractors as needed
            
        elif component_type == 'transformer':
            if component_class == 'DataCleaner':
                return DataCleaner(component_name, config=component_config)
            elif component_class == 'LibraryDataTransformer':
                return LibraryDataTransformer(component_name, config=component_config)
            # Add more transformers as needed
            
        elif component_type == 'loader':
            if component_class == 'DatabaseLoader':
                return DatabaseLoader(component_name, **component_params, config=component_config)
            elif component_class == 'CSVLoader':
                return CSVLoader(component_name, **component_params, config=component_config)
            elif component_class == 'LibraryTableLoader':
                return LibraryTableLoader(component_name, **component_params, config=component_config)
            # Add more loaders as needed
        
        raise ValueError(f"Unknown component: {component_type}.{component_class}")
    
    def _update_pipeline_metrics(self, scheduled_pipeline: ScheduledPipeline, results: Dict[str, Any]):
        """Update pipeline execution metrics"""
        try:
            conn = sqlite3.connect(self.metrics_db_path)
            
            # Insert execution record
            conn.execute("""
                INSERT INTO pipeline_executions 
                (pipeline_name, execution_id, start_time, end_time, status, duration_seconds, records_processed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                scheduled_pipeline.name,
                results.get('execution_id'),
                results.get('start_time'),
                results.get('end_time'),
                results.get('status'),
                results.get('duration'),
                sum(component.get('records_processed', 0) for component in results.get('component_metrics', []))
            ))
            
            # Insert metrics
            metrics = [
                ('duration_seconds', results.get('duration', 0), 'performance'),
                ('success_rate', scheduled_pipeline.success_count / max(scheduled_pipeline.run_count, 1), 'quality'),
                ('total_runs', scheduled_pipeline.run_count, 'usage'),
                ('total_failures', scheduled_pipeline.failure_count, 'quality')
            ]
            
            for metric_name, metric_value, metric_type in metrics:
                conn.execute("""
                    INSERT INTO pipeline_metrics (pipeline_name, metric_name, metric_value, metric_type)
                    VALUES (?, ?, ?, ?)
                """, (scheduled_pipeline.name, metric_name, metric_value, metric_type))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update pipeline metrics: {e}")
    
    def _log_scheduler_event(self, event_type: str, pipeline_name: str = None, 
                           message: str = "", details: str = ""):
        """Log scheduler event"""
        try:
            conn = sqlite3.connect(self.metrics_db_path)
            conn.execute("""
                INSERT INTO scheduler_events (event_type, pipeline_name, message, details)
                VALUES (?, ?, ?, ?)
            """, (event_type, pipeline_name, message, details))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log scheduler event: {e}")
    
    def start_scheduler(self):
        """Start the pipeline scheduler"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Scheduler is already running")
            return
        
        # Schedule all enabled pipelines
        for scheduled_pipeline in self.scheduled_pipelines.values():
            self._schedule_pipeline(scheduled_pipeline)
        
        # Start scheduler thread
        self.stop_scheduler = False
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self._log_scheduler_event("scheduler_started", message="Pipeline scheduler started")
        logger.info("Pipeline scheduler started")
    
    def stop_scheduler(self):
        """Stop the pipeline scheduler"""
        self.stop_scheduler = True
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        self._log_scheduler_event("scheduler_stopped", message="Pipeline scheduler stopped")
        logger.info("Pipeline scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while not self.stop_scheduler:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(5)
    
    def get_pipeline_status(self, pipeline_name: str = None) -> Dict[str, Any]:
        """Get status of pipelines"""
        if pipeline_name:
            if pipeline_name in self.scheduled_pipelines:
                pipeline = self.scheduled_pipelines[pipeline_name]
                return {
                    'name': pipeline.name,
                    'status': pipeline.status.value,
                    'enabled': pipeline.enabled,
                    'last_run': pipeline.last_run,
                    'next_run': pipeline.next_run,
                    'run_count': pipeline.run_count,
                    'success_count': pipeline.success_count,
                    'failure_count': pipeline.failure_count,
                    'success_rate': pipeline.success_count / max(pipeline.run_count, 1)
                }
            else:
                return {'error': f'Pipeline not found: {pipeline_name}'}
        else:
            # Return status of all pipelines
            return {
                name: {
                    'status': pipeline.status.value,
                    'enabled': pipeline.enabled,
                    'last_run': pipeline.last_run,
                    'run_count': pipeline.run_count,
                    'success_rate': pipeline.success_count / max(pipeline.run_count, 1)
                }
                for name, pipeline in self.scheduled_pipelines.items()
            }
    
    def enable_pipeline(self, pipeline_name: str):
        """Enable a scheduled pipeline"""
        if pipeline_name in self.scheduled_pipelines:
            self.scheduled_pipelines[pipeline_name].enabled = True
            self._schedule_pipeline(self.scheduled_pipelines[pipeline_name])
            self._save_pipeline_configs()
            logger.info(f"Enabled pipeline: {pipeline_name}")
        else:
            raise ValueError(f"Pipeline not found: {pipeline_name}")
    
    def disable_pipeline(self, pipeline_name: str):
        """Disable a scheduled pipeline"""
        if pipeline_name in self.scheduled_pipelines:
            self.scheduled_pipelines[pipeline_name].enabled = False
            schedule.clear(pipeline_name)
            self._save_pipeline_configs()
            logger.info(f"Disabled pipeline: {pipeline_name}")
        else:
            raise ValueError(f"Pipeline not found: {pipeline_name}")
    
    def _save_pipeline_configs(self):
        """Save pipeline configurations to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            configs = {}
            for name, pipeline in self.scheduled_pipelines.items():
                configs[name] = {
                    'pipeline': pipeline.pipeline_config,
                    'schedule': pipeline.schedule_config,
                    'enabled': pipeline.enabled
                }
            
            with open(self.config_file, 'w') as f:
                json.dump(configs, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save pipeline configurations: {e}")
    
    def get_metrics(self, pipeline_name: str = None, days: int = 7) -> Dict[str, Any]:
        """Get pipeline metrics"""
        try:
            conn = sqlite3.connect(self.metrics_db_path)
            
            # Base query conditions
            conditions = ["timestamp >= datetime('now', '-{} days')".format(days)]
            params = []
            
            if pipeline_name:
                conditions.append("pipeline_name = ?")
                params.append(pipeline_name)
            
            where_clause = " AND ".join(conditions)
            
            # Get execution metrics
            execution_query = f"""
                SELECT 
                    pipeline_name,
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_executions,
                    AVG(duration_seconds) as avg_duration,
                    SUM(records_processed) as total_records_processed
                FROM pipeline_executions
                WHERE {where_clause}
                GROUP BY pipeline_name
            """
            
            executions_df = pd.read_sql_query(execution_query, conn, params=params)
            
            # Get latest metrics
            metrics_query = f"""
                SELECT pipeline_name, metric_name, metric_value, metric_type
                FROM pipeline_metrics pm1
                WHERE {where_clause}
                AND timestamp = (
                    SELECT MAX(timestamp) 
                    FROM pipeline_metrics pm2 
                    WHERE pm2.pipeline_name = pm1.pipeline_name 
                    AND pm2.metric_name = pm1.metric_name
                )
            """
            
            metrics_df = pd.read_sql_query(metrics_query, conn, params=params)
            
            conn.close()
            
            return {
                'executions': executions_df.to_dict('records'),
                'metrics': metrics_df.to_dict('records'),
                'summary': {
                    'total_pipelines': len(self.scheduled_pipelines),
                    'active_pipelines': len([p for p in self.scheduled_pipelines.values() if p.enabled]),
                    'running_pipelines': len(self.running_pipelines)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {'error': str(e)}

# Default pipeline configurations
DEFAULT_PIPELINE_CONFIGS = {
    'library_daily_sync': {
        'pipeline': {
            'extractors': [
                {
                    'name': 'library_transactions_extractor',
                    'class': 'LibraryDataExtractor',
                    'params': {
                        'db_path': 'notebooks/library.db'
                    },
                    'config': {
                        'extraction_type': 'transactions',
                        'date_range': {
                            'start_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                        }
                    }
                }
            ],
            'transformers': [
                {
                    'name': 'library_transactions_transformer',
                    'class': 'LibraryDataTransformer',
                    'params': {},
                    'config': {
                        'data_type': 'transactions'
                    }
                }
            ],
            'loaders': [
                {
                    'name': 'transactions_staging_loader',
                    'class': 'LibraryTableLoader',
                    'params': {
                        'db_path': 'notebooks/library.db',
                        'table_type': 'transactions'
                    },
                    'config': {}
                }
            ]
        },
        'schedule': {
            'type': 'daily',
            'time': '02:00'
        },
        'enabled': True
    },
    'library_weekly_cleanup': {
        'pipeline': {
            'extractors': [
                {
                    'name': 'library_full_extractor',
                    'class': 'LibraryDataExtractor',
                    'params': {
                        'db_path': 'notebooks/library.db'
                    },
                    'config': {
                        'extraction_type': 'full'
                    }
                }
            ],
            'transformers': [
                {
                    'name': 'library_data_cleaner',
                    'class': 'DataCleaner',
                    'params': {},
                    'config': {
                        'auto_clean': True,
                        'cleaning_rules': [
                            {'type': 'remove_nulls', 'threshold': 0.8},
                            {'type': 'standardize_email', 'column': 'member_email'},
                            {'type': 'standardize_phone', 'column': 'member_phone'}
                        ]
                    }
                }
            ],
            'loaders': [
                {
                    'name': 'cleaned_data_backup',
                    'class': 'CSVLoader',
                    'params': {
                        'file_path': f'data/processed/library_cleaned_{datetime.now().strftime("%Y%m%d")}.csv'
                    },
                    'config': {
                        'create_backup': True
                    }
                }
            ]
        },
        'schedule': {
            'type': 'weekly',
            'day': 'sunday',
            'time': '01:00'
        },
        'enabled': True
    }
}

def create_default_scheduler_config():
    """Create default scheduler configuration file"""
    config_file = "schedulers/pipeline_schedules.json"
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(DEFAULT_PIPELINE_CONFIGS, f, indent=2, default=str)
    
    print(f"✅ Created default scheduler configuration: {config_file}")

if __name__ == "__main__":
    print("⏰ Pipeline Scheduler & Orchestrator Ready")
    print("Available commands:")
    print("  - create_default_scheduler_config(): Create default configuration")
    print("  - PipelineScheduler(): Main scheduler class")
    
    # Create default config if it doesn't exist
    if not os.path.exists("schedulers/pipeline_schedules.json"):
        create_default_scheduler_config()
