#!/usr/bin/env python3
"""
Phase 4: Data Pipeline & ETL Infrastructure
Core ETL Pipeline Framework for Library Analytics System
"""

import os
import sys
import json
import logging
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import hashlib
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ETLPipelineError(Exception):
    """Custom exception for ETL pipeline errors"""
    pass

class DataQualityError(ETLPipelineError):
    """Exception for data quality issues"""
    pass

class BaseETLComponent(ABC):
    """Base class for all ETL components"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'duration': None,
            'status': 'pending',
            'records_processed': 0,
            'errors': [],
            'warnings': []
        }
    
    def start_execution(self):
        """Start component execution and record metrics"""
        self.metrics['start_time'] = datetime.now()
        self.metrics['status'] = 'running'
        self.logger.info(f"Starting {self.name}")
    
    def end_execution(self, status: str = 'completed'):
        """End component execution and record metrics"""
        self.metrics['end_time'] = datetime.now()
        self.metrics['duration'] = (self.metrics['end_time'] - self.metrics['start_time']).total_seconds()
        self.metrics['status'] = status
        self.logger.info(f"Completed {self.name} in {self.metrics['duration']:.2f}s")
    
    def add_error(self, error: str):
        """Add error to metrics"""
        self.metrics['errors'].append(error)
        self.logger.error(f"{self.name}: {error}")
    
    def add_warning(self, warning: str):
        """Add warning to metrics"""
        self.metrics['warnings'].append(warning)
        self.logger.warning(f"{self.name}: {warning}")
    
    @abstractmethod
    def execute(self, data: Any = None) -> Any:
        """Execute the component logic"""
        pass

class DataExtractor(BaseETLComponent):
    """Base class for data extraction components"""
    
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Extract data and return as DataFrame"""
        pass
    
    def execute(self, data: Any = None) -> pd.DataFrame:
        """Execute extraction"""
        self.start_execution()
        try:
            result = self.extract()
            self.metrics['records_processed'] = len(result)
            self.end_execution()
            return result
        except Exception as e:
            self.add_error(str(e))
            self.end_execution('failed')
            raise ETLPipelineError(f"Extraction failed: {e}")

class DataTransformer(BaseETLComponent):
    """Base class for data transformation components"""
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data and return processed DataFrame"""
        pass
    
    def execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """Execute transformation"""
        self.start_execution()
        try:
            result = self.transform(data)
            self.metrics['records_processed'] = len(result)
            self.end_execution()
            return result
        except Exception as e:
            self.add_error(str(e))
            self.end_execution('failed')
            raise ETLPipelineError(f"Transformation failed: {e}")

class DataLoader(BaseETLComponent):
    """Base class for data loading components"""
    
    @abstractmethod
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to destination"""
        pass
    
    def execute(self, data: pd.DataFrame) -> bool:
        """Execute loading"""
        self.start_execution()
        try:
            result = self.load(data)
            self.metrics['records_processed'] = len(data)
            self.end_execution()
            return result
        except Exception as e:
            self.add_error(str(e))
            self.end_execution('failed')
            raise ETLPipelineError(f"Loading failed: {e}")

class DataQualityValidator(BaseETLComponent):
    """Data quality validation component"""
    
    def __init__(self, name: str, rules: List[Dict[str, Any]], config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.rules = rules
    
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate data against quality rules"""
        validation_results = {
            'passed': True,
            'total_rules': len(self.rules),
            'passed_rules': 0,
            'failed_rules': 0,
            'rule_results': [],
            'data_profile': self._profile_data(data)
        }
        
        for rule in self.rules:
            rule_result = self._validate_rule(data, rule)
            validation_results['rule_results'].append(rule_result)
            
            if rule_result['passed']:
                validation_results['passed_rules'] += 1
            else:
                validation_results['failed_rules'] += 1
                if rule.get('severity', 'warning') == 'error':
                    validation_results['passed'] = False
        
        return validation_results
    
    def _validate_rule(self, data: pd.DataFrame, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single rule"""
        rule_type = rule['type']
        rule_name = rule['name']
        
        try:
            if rule_type == 'not_null':
                column = rule['column']
                null_count = data[column].isnull().sum()
                passed = null_count == 0
                message = f"Column '{column}' has {null_count} null values"
                
            elif rule_type == 'unique':
                column = rule['column']
                duplicate_count = data.duplicated(subset=[column]).sum()
                passed = duplicate_count == 0
                message = f"Column '{column}' has {duplicate_count} duplicate values"
                
            elif rule_type == 'range':
                column = rule['column']
                min_val = rule.get('min')
                max_val = rule.get('max')
                out_of_range = 0
                
                if min_val is not None:
                    out_of_range += (data[column] < min_val).sum()
                if max_val is not None:
                    out_of_range += (data[column] > max_val).sum()
                
                passed = out_of_range == 0
                message = f"Column '{column}' has {out_of_range} values out of range [{min_val}, {max_val}]"
                
            elif rule_type == 'pattern':
                column = rule['column']
                pattern = rule['pattern']
                invalid_count = (~data[column].astype(str).str.match(pattern)).sum()
                passed = invalid_count == 0
                message = f"Column '{column}' has {invalid_count} values not matching pattern '{pattern}'"
                
            elif rule_type == 'completeness':
                threshold = rule.get('threshold', 0.95)
                total_cells = data.size
                non_null_cells = data.count().sum()
                completeness = non_null_cells / total_cells if total_cells > 0 else 0
                passed = completeness >= threshold
                message = f"Data completeness is {completeness:.2%} (threshold: {threshold:.2%})"
                
            else:
                passed = False
                message = f"Unknown rule type: {rule_type}"
                
            return {
                'rule_name': rule_name,
                'rule_type': rule_type,
                'passed': passed,
                'message': message,
                'severity': rule.get('severity', 'warning')
            }
            
        except Exception as e:
            return {
                'rule_name': rule_name,
                'rule_type': rule_type,
                'passed': False,
                'message': f"Rule execution failed: {str(e)}",
                'severity': 'error'
            }
    
    def _profile_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate data profile"""
        return {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'memory_usage_mb': data.memory_usage(deep=True).sum() / 1024 / 1024,
            'null_counts': data.isnull().sum().to_dict(),
            'dtypes': data.dtypes.astype(str).to_dict(),
            'duplicates': data.duplicated().sum()
        }
    
    def execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """Execute validation"""
        self.start_execution()
        try:
            results = self.validate(data)
            
            if not results['passed']:
                failed_errors = [r for r in results['rule_results'] 
                               if not r['passed'] and r['severity'] == 'error']
                if failed_errors:
                    error_msg = f"Data quality validation failed: {len(failed_errors)} critical errors"
                    self.add_error(error_msg)
                    self.end_execution('failed')
                    raise DataQualityError(error_msg)
            
            # Log warnings
            failed_warnings = [r for r in results['rule_results'] 
                             if not r['passed'] and r['severity'] == 'warning']
            for warning in failed_warnings:
                self.add_warning(warning['message'])
            
            self.metrics['validation_results'] = results
            self.end_execution()
            return data
            
        except DataQualityError:
            raise
        except Exception as e:
            self.add_error(str(e))
            self.end_execution('failed')
            raise ETLPipelineError(f"Validation failed: {e}")

class ETLPipeline:
    """Main ETL Pipeline orchestrator"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.components = []
        self.logger = logging.getLogger(f"{__name__}.ETLPipeline")
        self.execution_id = hashlib.md5(f"{name}_{datetime.now()}".encode()).hexdigest()
        self.pipeline_metrics = {
            'execution_id': self.execution_id,
            'pipeline_name': name,
            'start_time': None,
            'end_time': None,
            'duration': None,
            'status': 'pending',
            'total_components': 0,
            'successful_components': 0,
            'failed_components': 0,
            'component_metrics': []
        }
    
    def add_component(self, component: BaseETLComponent):
        """Add component to pipeline"""
        self.components.append(component)
        self.pipeline_metrics['total_components'] += 1
    
    def execute(self) -> Dict[str, Any]:
        """Execute the entire pipeline"""
        self.pipeline_metrics['start_time'] = datetime.now()
        self.pipeline_metrics['status'] = 'running'
        
        self.logger.info(f"Starting pipeline: {self.name} (ID: {self.execution_id})")
        
        data = None
        
        try:
            for component in self.components:
                self.logger.info(f"Executing component: {component.name}")
                
                try:
                    data = component.execute(data)
                    self.pipeline_metrics['successful_components'] += 1
                    
                except Exception as e:
                    self.pipeline_metrics['failed_components'] += 1
                    self.logger.error(f"Component {component.name} failed: {e}")
                    
                    if self.config.get('stop_on_error', True):
                        self.pipeline_metrics['status'] = 'failed'
                        raise ETLPipelineError(f"Pipeline failed at component {component.name}: {e}")
                
                finally:
                    self.pipeline_metrics['component_metrics'].append(component.metrics)
            
            self.pipeline_metrics['status'] = 'completed'
            self.logger.info(f"Pipeline {self.name} completed successfully")
            
        except Exception as e:
            self.pipeline_metrics['status'] = 'failed'
            self.logger.error(f"Pipeline {self.name} failed: {e}")
            
        finally:
            self.pipeline_metrics['end_time'] = datetime.now()
            self.pipeline_metrics['duration'] = (
                self.pipeline_metrics['end_time'] - self.pipeline_metrics['start_time']
            ).total_seconds()
            
            # Save pipeline execution results
            self._save_execution_results()
        
        return self.pipeline_metrics
    
    def _save_execution_results(self):
        """Save pipeline execution results"""
        try:
            results_file = f"monitoring/pipeline_execution_{self.execution_id}.json"
            with open(results_file, 'w') as f:
                json.dump(self.pipeline_metrics, f, default=str, indent=2)
                
            self.logger.info(f"Pipeline results saved to: {results_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save pipeline results: {e}")

if __name__ == "__main__":
    print("🏗️ ETL Pipeline Framework Initialized")
    print("This is the core framework for Phase 4: Data Pipeline & ETL Infrastructure")
    print("Use this framework to build specific extractors, transformers, and loaders.")
