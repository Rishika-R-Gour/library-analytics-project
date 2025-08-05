#!/usr/bin/env python3
"""
ETL Pipeline Monitoring and Quality Assurance System
Provides comprehensive monitoring, alerting, and quality metrics for data pipelines
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
import hashlib
import statistics
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/data_quality.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of quality metrics"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"

@dataclass
class QualityMetric:
    """Represents a data quality metric"""
    name: str
    value: float
    threshold: float
    metric_type: MetricType
    status: str
    message: str
    timestamp: datetime

@dataclass
class Alert:
    """Represents a monitoring alert"""
    id: str
    level: AlertLevel
    title: str
    message: str
    pipeline_name: str
    metric_name: str
    threshold: float
    actual_value: float
    timestamp: datetime
    acknowledged: bool = False

class DataQualityMonitor:
    """Comprehensive data quality monitoring system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_path = self.config.get('db_path', 'monitoring/quality_metrics.db')
        self.alert_thresholds = self.config.get('alert_thresholds', {})
        self.quality_rules = self.config.get('quality_rules', [])
        
        # Initialize monitoring database
        self._init_monitoring_db()
        
        # Default quality thresholds
        self.default_thresholds = {
            'completeness': 0.95,
            'accuracy': 0.98,
            'consistency': 0.95,
            'timeliness': 24,  # hours
            'validity': 0.99,
            'uniqueness': 0.98
        }
    
    def _init_monitoring_db(self):
        """Initialize monitoring database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            
            # Quality metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_name TEXT NOT NULL,
                    table_name TEXT,
                    metric_name TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    threshold_value REAL,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Alerts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    level TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    pipeline_name TEXT NOT NULL,
                    metric_name TEXT,
                    threshold_value REAL,
                    actual_value REAL,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    acknowledged_at TIMESTAMP,
                    acknowledged_by TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Data profiles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_name TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    data_type TEXT,
                    null_count INTEGER,
                    null_percentage REAL,
                    unique_count INTEGER,
                    unique_percentage REAL,
                    min_value TEXT,
                    max_value TEXT,
                    mean_value REAL,
                    median_value REAL,
                    std_dev REAL,
                    sample_values TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Pipeline health table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_name TEXT NOT NULL,
                    execution_id TEXT,
                    health_score REAL NOT NULL,
                    data_freshness_hours REAL,
                    records_processed INTEGER,
                    error_count INTEGER,
                    warning_count INTEGER,
                    quality_score REAL,
                    performance_score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Monitoring database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring database: {e}")
    
    def analyze_data_quality(self, data: pd.DataFrame, pipeline_name: str, 
                           table_name: str = None) -> List[QualityMetric]:
        """Comprehensive data quality analysis"""
        metrics = []
        
        try:
            # Completeness metrics
            completeness_metrics = self._analyze_completeness(data, pipeline_name, table_name)
            metrics.extend(completeness_metrics)
            
            # Validity metrics
            validity_metrics = self._analyze_validity(data, pipeline_name, table_name)
            metrics.extend(validity_metrics)
            
            # Uniqueness metrics
            uniqueness_metrics = self._analyze_uniqueness(data, pipeline_name, table_name)
            metrics.extend(uniqueness_metrics)
            
            # Consistency metrics
            consistency_metrics = self._analyze_consistency(data, pipeline_name, table_name)
            metrics.extend(consistency_metrics)
            
            # Store metrics in database
            self._store_quality_metrics(metrics)
            
            # Generate alerts for failed metrics
            self._generate_alerts(metrics, pipeline_name)
            
            # Create data profile
            self._create_data_profile(data, pipeline_name, table_name)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to analyze data quality: {e}")
            return []
    
    def _analyze_completeness(self, data: pd.DataFrame, pipeline_name: str, 
                            table_name: str) -> List[QualityMetric]:
        """Analyze data completeness"""
        metrics = []
        threshold = self.alert_thresholds.get('completeness', self.default_thresholds['completeness'])
        
        # Overall completeness
        total_cells = data.size
        non_null_cells = data.count().sum()
        completeness = non_null_cells / total_cells if total_cells > 0 else 0
        
        status = "pass" if completeness >= threshold else "fail"
        message = f"Overall data completeness: {completeness:.2%}"
        
        metrics.append(QualityMetric(
            name="overall_completeness",
            value=completeness,
            threshold=threshold,
            metric_type=MetricType.COMPLETENESS,
            status=status,
            message=message,
            timestamp=datetime.now()
        ))
        
        # Column-wise completeness
        for column in data.columns:
            column_completeness = data[column].count() / len(data) if len(data) > 0 else 0
            status = "pass" if column_completeness >= threshold else "fail"
            message = f"Column '{column}' completeness: {column_completeness:.2%}"
            
            metrics.append(QualityMetric(
                name=f"completeness_{column}",
                value=column_completeness,
                threshold=threshold,
                metric_type=MetricType.COMPLETENESS,
                status=status,
                message=message,
                timestamp=datetime.now()
            ))
        
        return metrics
    
    def _analyze_validity(self, data: pd.DataFrame, pipeline_name: str, 
                         table_name: str) -> List[QualityMetric]:
        """Analyze data validity"""
        metrics = []
        threshold = self.alert_thresholds.get('validity', self.default_thresholds['validity'])
        
        # Email validation
        email_columns = [col for col in data.columns if 'email' in col.lower()]
        for column in email_columns:
            if column in data.columns:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                valid_emails = data[column].astype(str).str.match(email_pattern, na=False)
                validity = valid_emails.sum() / data[column].count() if data[column].count() > 0 else 0
                
                status = "pass" if validity >= threshold else "fail"
                message = f"Email validity for '{column}': {validity:.2%}"
                
                metrics.append(QualityMetric(
                    name=f"email_validity_{column}",
                    value=validity,
                    threshold=threshold,
                    metric_type=MetricType.VALIDITY,
                    status=status,
                    message=message,
                    timestamp=datetime.now()
                ))
        
        # Phone validation
        phone_columns = [col for col in data.columns if 'phone' in col.lower()]
        for column in phone_columns:
            if column in data.columns:
                phone_pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
                valid_phones = data[column].astype(str).str.match(phone_pattern, na=False)
                validity = valid_phones.sum() / data[column].count() if data[column].count() > 0 else 0
                
                status = "pass" if validity >= threshold else "fail"
                message = f"Phone validity for '{column}': {validity:.2%}"
                
                metrics.append(QualityMetric(
                    name=f"phone_validity_{column}",
                    value=validity,
                    threshold=threshold,
                    metric_type=MetricType.VALIDITY,
                    status=status,
                    message=message,
                    timestamp=datetime.now()
                ))
        
        # Date validation
        date_columns = [col for col in data.columns if any(date_word in col.lower() 
                                                          for date_word in ['date', 'time', 'created', 'updated'])]
        for column in date_columns:
            if column in data.columns:
                try:
                    valid_dates = pd.to_datetime(data[column], errors='coerce').notna()
                    validity = valid_dates.sum() / data[column].count() if data[column].count() > 0 else 0
                    
                    status = "pass" if validity >= threshold else "fail"
                    message = f"Date validity for '{column}': {validity:.2%}"
                    
                    metrics.append(QualityMetric(
                        name=f"date_validity_{column}",
                        value=validity,
                        threshold=threshold,
                        metric_type=MetricType.VALIDITY,
                        status=status,
                        message=message,
                        timestamp=datetime.now()
                    ))
                except:
                    pass
        
        return metrics
    
    def _analyze_uniqueness(self, data: pd.DataFrame, pipeline_name: str, 
                           table_name: str) -> List[QualityMetric]:
        """Analyze data uniqueness"""
        metrics = []
        threshold = self.alert_thresholds.get('uniqueness', self.default_thresholds['uniqueness'])
        
        # Check columns that should be unique
        unique_columns = [col for col in data.columns if any(unique_word in col.lower() 
                                                           for unique_word in ['id', 'email', 'isbn', 'code'])]
        
        for column in unique_columns:
            if column in data.columns:
                unique_count = data[column].nunique()
                total_count = data[column].count()
                uniqueness = unique_count / total_count if total_count > 0 else 0
                
                status = "pass" if uniqueness >= threshold else "fail"
                message = f"Uniqueness for '{column}': {uniqueness:.2%} ({unique_count}/{total_count})"
                
                metrics.append(QualityMetric(
                    name=f"uniqueness_{column}",
                    value=uniqueness,
                    threshold=threshold,
                    metric_type=MetricType.UNIQUENESS,
                    status=status,
                    message=message,
                    timestamp=datetime.now()
                ))
        
        # Overall row uniqueness
        duplicate_rows = data.duplicated().sum()
        row_uniqueness = (len(data) - duplicate_rows) / len(data) if len(data) > 0 else 0
        
        status = "pass" if row_uniqueness >= threshold else "fail"
        message = f"Row uniqueness: {row_uniqueness:.2%} ({duplicate_rows} duplicates)"
        
        metrics.append(QualityMetric(
            name="row_uniqueness",
            value=row_uniqueness,
            threshold=threshold,
            metric_type=MetricType.UNIQUENESS,
            status=status,
            message=message,
            timestamp=datetime.now()
        ))
        
        return metrics
    
    def _analyze_consistency(self, data: pd.DataFrame, pipeline_name: str, 
                           table_name: str) -> List[QualityMetric]:
        """Analyze data consistency"""
        metrics = []
        threshold = self.alert_thresholds.get('consistency', self.default_thresholds['consistency'])
        
        # Check referential integrity (if foreign key columns exist)
        foreign_key_columns = [col for col in data.columns if col.endswith('_id')]
        
        for column in foreign_key_columns:
            if column in data.columns:
                # Check for null foreign keys
                non_null_fks = data[column].count()
                total_fks = len(data)
                consistency = non_null_fks / total_fks if total_fks > 0 else 0
                
                status = "pass" if consistency >= threshold else "fail"
                message = f"Foreign key consistency for '{column}': {consistency:.2%}"
                
                metrics.append(QualityMetric(
                    name=f"fk_consistency_{column}",
                    value=consistency,
                    threshold=threshold,
                    metric_type=MetricType.CONSISTENCY,
                    status=status,
                    message=message,
                    timestamp=datetime.now()
                ))
        
        # Check data type consistency
        for column in data.columns:
            try:
                # Count non-null values that match expected type
                if data[column].dtype in ['int64', 'float64']:
                    consistent_values = pd.to_numeric(data[column], errors='coerce').notna()
                elif data[column].dtype == 'object':
                    # For string columns, check if they're consistently formatted
                    consistent_values = data[column].astype(str).str.len() > 0
                else:
                    continue
                
                consistency = consistent_values.sum() / data[column].count() if data[column].count() > 0 else 0
                
                status = "pass" if consistency >= threshold else "fail"
                message = f"Type consistency for '{column}': {consistency:.2%}"
                
                metrics.append(QualityMetric(
                    name=f"type_consistency_{column}",
                    value=consistency,
                    threshold=threshold,
                    metric_type=MetricType.CONSISTENCY,
                    status=status,
                    message=message,
                    timestamp=datetime.now()
                ))
                
            except:
                continue
        
        return metrics
    
    def _store_quality_metrics(self, metrics: List[QualityMetric]):
        """Store quality metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            for metric in metrics:
                conn.execute("""
                    INSERT INTO quality_metrics 
                    (pipeline_name, metric_name, metric_type, metric_value, threshold_value, status, message, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    'current_pipeline',  # This should be passed as parameter
                    metric.name,
                    metric.metric_type.value,
                    metric.value,
                    metric.threshold,
                    metric.status,
                    metric.message,
                    metric.timestamp
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store quality metrics: {e}")
    
    def _generate_alerts(self, metrics: List[QualityMetric], pipeline_name: str):
        """Generate alerts for failed quality metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            for metric in metrics:
                if metric.status == "fail":
                    # Determine alert level based on severity
                    if metric.value < metric.threshold * 0.5:
                        alert_level = AlertLevel.CRITICAL
                    elif metric.value < metric.threshold * 0.8:
                        alert_level = AlertLevel.ERROR
                    else:
                        alert_level = AlertLevel.WARNING
                    
                    # Create alert ID
                    alert_id = hashlib.md5(f"{pipeline_name}_{metric.name}_{metric.timestamp}".encode()).hexdigest()
                    
                    # Create alert
                    alert = Alert(
                        id=alert_id,
                        level=alert_level,
                        title=f"Data Quality Alert: {metric.name}",
                        message=f"{metric.message} (Threshold: {metric.threshold:.2%})",
                        pipeline_name=pipeline_name,
                        metric_name=metric.name,
                        threshold=metric.threshold,
                        actual_value=metric.value,
                        timestamp=metric.timestamp
                    )
                    
                    # Store alert
                    conn.execute("""
                        INSERT OR REPLACE INTO alerts 
                        (id, level, title, message, pipeline_name, metric_name, threshold_value, actual_value, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        alert.id,
                        alert.level.value,
                        alert.title,
                        alert.message,
                        alert.pipeline_name,
                        alert.metric_name,
                        alert.threshold,
                        alert.actual_value,
                        alert.timestamp
                    ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to generate alerts: {e}")
    
    def _create_data_profile(self, data: pd.DataFrame, pipeline_name: str, table_name: str):
        """Create comprehensive data profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            for column in data.columns:
                profile = self._profile_column(data[column])
                
                conn.execute("""
                    INSERT INTO data_profiles 
                    (pipeline_name, table_name, column_name, data_type, null_count, null_percentage,
                     unique_count, unique_percentage, min_value, max_value, mean_value, median_value,
                     std_dev, sample_values, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pipeline_name,
                    table_name or 'unknown',
                    column,
                    str(data[column].dtype),
                    profile['null_count'],
                    profile['null_percentage'],
                    profile['unique_count'],
                    profile['unique_percentage'],
                    profile['min_value'],
                    profile['max_value'],
                    profile['mean_value'],
                    profile['median_value'],
                    profile['std_dev'],
                    json.dumps(profile['sample_values']),
                    datetime.now()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to create data profile: {e}")
    
    def _profile_column(self, series: pd.Series) -> Dict[str, Any]:
        """Create profile for a single column"""
        profile = {
            'null_count': series.isnull().sum(),
            'null_percentage': series.isnull().sum() / len(series) if len(series) > 0 else 0,
            'unique_count': series.nunique(),
            'unique_percentage': series.nunique() / len(series) if len(series) > 0 else 0,
            'min_value': None,
            'max_value': None,
            'mean_value': None,
            'median_value': None,
            'std_dev': None,
            'sample_values': []
        }
        
        try:
            # Numeric statistics
            if series.dtype in ['int64', 'float64']:
                profile['min_value'] = float(series.min()) if not series.empty else None
                profile['max_value'] = float(series.max()) if not series.empty else None
                profile['mean_value'] = float(series.mean()) if not series.empty else None
                profile['median_value'] = float(series.median()) if not series.empty else None
                profile['std_dev'] = float(series.std()) if not series.empty else None
            else:
                # String statistics
                profile['min_value'] = str(series.min()) if not series.empty else None
                profile['max_value'] = str(series.max()) if not series.empty else None
            
            # Sample values
            sample_size = min(10, len(series.dropna()))
            if sample_size > 0:
                profile['sample_values'] = series.dropna().head(sample_size).astype(str).tolist()
            
        except:
            pass
        
        return profile
    
    def calculate_pipeline_health_score(self, pipeline_name: str, execution_id: str = None) -> float:
        """Calculate overall pipeline health score"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get recent quality metrics
            query = """
                SELECT metric_type, AVG(metric_value) as avg_value
                FROM quality_metrics
                WHERE pipeline_name = ? AND timestamp >= datetime('now', '-24 hours')
                GROUP BY metric_type
            """
            
            metrics_df = pd.read_sql_query(query, conn, params=[pipeline_name])
            
            if metrics_df.empty:
                return 1.0  # No data means perfect health (neutral)
            
            # Calculate weighted health score
            weights = {
                'completeness': 0.25,
                'accuracy': 0.25,
                'validity': 0.20,
                'consistency': 0.15,
                'uniqueness': 0.15
            }
            
            weighted_score = 0
            total_weight = 0
            
            for _, row in metrics_df.iterrows():
                metric_type = row['metric_type']
                avg_value = row['avg_value']
                weight = weights.get(metric_type, 0.1)
                
                weighted_score += avg_value * weight
                total_weight += weight
            
            health_score = weighted_score / total_weight if total_weight > 0 else 1.0
            
            # Store health score
            conn.execute("""
                INSERT INTO pipeline_health (pipeline_name, execution_id, health_score, timestamp)
                VALUES (?, ?, ?, ?)
            """, (pipeline_name, execution_id, health_score, datetime.now()))
            
            conn.commit()
            conn.close()
            
            return health_score
            
        except Exception as e:
            logger.error(f"Failed to calculate pipeline health score: {e}")
            return 0.0
    
    def get_quality_report(self, pipeline_name: str = None, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Base conditions
            conditions = ["timestamp >= datetime('now', '-{} days')".format(days)]
            params = []
            
            if pipeline_name:
                conditions.append("pipeline_name = ?")
                params.append(pipeline_name)
            
            where_clause = " AND ".join(conditions)
            
            # Get quality metrics summary
            metrics_query = f"""
                SELECT 
                    metric_type,
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) as passed_checks,
                    AVG(metric_value) as avg_value,
                    MIN(metric_value) as min_value,
                    MAX(metric_value) as max_value
                FROM quality_metrics
                WHERE {where_clause}
                GROUP BY metric_type
            """
            
            metrics_df = pd.read_sql_query(metrics_query, conn, params=params)
            
            # Get active alerts
            alerts_query = f"""
                SELECT level, COUNT(*) as count
                FROM alerts
                WHERE acknowledged = FALSE AND {where_clause.replace('timestamp', 'alerts.timestamp')}
                GROUP BY level
            """
            
            alerts_df = pd.read_sql_query(alerts_query, conn, params=params)
            
            # Get pipeline health trend
            health_query = f"""
                SELECT 
                    DATE(timestamp) as date,
                    AVG(health_score) as avg_health_score
                FROM pipeline_health
                WHERE {where_clause}
                GROUP BY DATE(timestamp)
                ORDER BY date
            """
            
            health_df = pd.read_sql_query(health_query, conn, params=params)
            
            conn.close()
            
            # Calculate overall scores
            overall_quality_score = metrics_df['avg_value'].mean() if not metrics_df.empty else 1.0
            overall_health_score = health_df['avg_health_score'].mean() if not health_df.empty else 1.0
            
            return {
                'summary': {
                    'overall_quality_score': overall_quality_score,
                    'overall_health_score': overall_health_score,
                    'total_quality_checks': metrics_df['total_checks'].sum() if not metrics_df.empty else 0,
                    'passed_quality_checks': metrics_df['passed_checks'].sum() if not metrics_df.empty else 0,
                    'active_alerts': alerts_df['count'].sum() if not alerts_df.empty else 0
                },
                'quality_metrics': metrics_df.to_dict('records'),
                'alerts_by_level': alerts_df.to_dict('records'),
                'health_trend': health_df.to_dict('records'),
                'report_period': f"Last {days} days",
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate quality report: {e}")
            return {'error': str(e)}
    
    def get_alerts(self, acknowledged: bool = False, level: str = None) -> List[Dict[str, Any]]:
        """Get alerts with filtering options"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            conditions = ["acknowledged = ?"]
            params = [acknowledged]
            
            if level:
                conditions.append("level = ?")
                params.append(level)
            
            where_clause = " AND ".join(conditions)
            
            query = f"""
                SELECT * FROM alerts
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT 100
            """
            
            alerts_df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return alerts_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system"):
        """Acknowledge an alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("""
                UPDATE alerts 
                SET acknowledged = TRUE, acknowledged_at = ?, acknowledged_by = ?
                WHERE id = ?
            """, (datetime.now(), acknowledged_by, alert_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")

def create_monitoring_dashboard_data():
    """Create sample data for monitoring dashboard"""
    monitor = DataQualityMonitor()
    
    # Sample data for testing
    sample_data = pd.DataFrame({
        'id': range(1, 101),
        'name': [f'Member {i}' for i in range(1, 101)],
        'email': [f'member{i}@library.com' if i % 10 != 0 else 'invalid_email' for i in range(1, 101)],
        'phone': [f'555-{i:04d}' if i % 15 != 0 else '12345' for i in range(1, 101)],
        'join_date': pd.date_range('2020-01-01', periods=100, freq='D'),
        'status': ['active' if i % 20 != 0 else None for i in range(1, 101)]
    })
    
    # Analyze quality
    metrics = monitor.analyze_data_quality(sample_data, 'test_pipeline', 'members')
    
    # Calculate health score
    health_score = monitor.calculate_pipeline_health_score('test_pipeline')
    
    print(f"✅ Generated {len(metrics)} quality metrics")
    print(f"📊 Pipeline health score: {health_score:.2%}")
    
    return monitor

if __name__ == "__main__":
    print("📋 ETL Monitoring & Quality Assurance System Ready")
    print("Available features:")
    print("  - DataQualityMonitor: Comprehensive quality analysis")
    print("  - Quality metrics tracking and alerting")
    print("  - Pipeline health scoring")
    print("  - Data profiling and anomaly detection")
    
    # Create sample monitoring data
    create_monitoring_dashboard_data()
