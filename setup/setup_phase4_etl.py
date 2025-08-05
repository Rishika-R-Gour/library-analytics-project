#!/usr/bin/env python3
"""
Phase 4: ETL Infrastructure Setup and Demo
Complete setup script for the Data Pipeline & ETL Infrastructure
"""

import os
import sys
import json
import subprocess
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our ETL components
from pipelines.etl_framework import ETLPipeline, DataQualityValidator
from pipelines.extractors.data_extractors import LibraryDataExtractor, CSVExtractor
from pipelines.transformers.data_transformers import LibraryDataTransformer, DataCleaner
from pipelines.loaders.data_loaders import CSVLoader, LibraryTableLoader, StagingLoader
from monitoring.quality_monitor import DataQualityMonitor

def setup_etl_infrastructure():
    """Set up the complete ETL infrastructure"""
    print("🏗️ Setting up Phase 4: ETL Infrastructure...")
    
    # 1. Create sample data files for testing
    print("\n📁 Creating sample data files...")
    create_sample_data_files()
    
    # 2. Initialize monitoring system
    print("\n📊 Initializing monitoring system...")
    monitor = DataQualityMonitor()
    
    # 3. Create default pipeline configurations
    print("\n⚙️ Creating pipeline configurations...")
    create_pipeline_configurations()
    
    # 4. Set up scheduling infrastructure
    print("\n⏰ Setting up scheduler infrastructure...")
    setup_scheduler_infrastructure()
    
    print("\n✅ ETL Infrastructure setup complete!")
    return monitor

def create_sample_data_files():
    """Create sample CSV files for ETL testing"""
    
    # Sample books data with quality issues for testing
    books_data = pd.DataFrame({
        'isbn': ['978-0123456789', '978-0987654321', '978-0555666777', '', '978-0123456789'],  # Duplicate and empty
        'title': ['Data Science Basics', 'Machine Learning Guide', 'Python Programming', 'Database Systems', 'Data Science Basics'],
        'author': ['John Smith', 'Jane Doe', '', 'Bob Johnson', 'John Smith'],  # Empty author
        'genre': ['Technology', 'technology', 'TECHNOLOGY', 'Computer Science', 'Technology'],  # Inconsistent case
        'publication_year': [2020, 2021, 2019, 1995, 2020],
        'price': [29.99, 45.50, None, 89.95, 29.99],  # Missing price
        'publisher': ['Tech Books', 'ML Press', 'Python House', 'CS Publishers', 'Tech Books'],
        'pages': [300, 450, 250, 800, 300],
        'language': ['English', 'English', 'English', 'English', 'English']
    })
    
    # Sample members data with quality issues
    members_data = pd.DataFrame({
        'member_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['Alice Johnson', 'Bob Smith', '', 'Diana Prince', 'Eve Wilson', 'Frank Miller', 'Grace Lee', 'Henry Ford', 'Ivy Chen', 'Jack Brown'],
        'email': ['alice@email.com', 'bob.smith@library.org', 'invalid-email', 'diana@books.com', '', 'frank@email.com', 'grace.lee@email.com', 'henry@invalid', 'ivy.chen@email.com', 'jack.brown@email.com'],
        'phone': ['(555) 123-4567', '555-987-6543', '12345', '(555) 111-2222', '', '555.333.4444', '(555) 555-5555', 'invalid-phone', '(555) 777-8888', '(555) 999-0000'],
        'join_date': ['2020-01-15', '2020-02-20', '2020-03-10', '2019-12-05', '2021-01-01', '2020-06-15', '2020-07-20', '2019-11-30', '2021-02-14', '2020-09-05'],
        'membership_type': ['Standard', 'Premium', 'standard', 'Premium', 'Standard', '', 'Premium', 'Standard', 'Premium', 'Standard'],
        'address': ['123 Main St', '456 Oak Ave', '789 Pine St', '', '321 Elm St', '654 Maple Dr', '987 Cedar Ln', '147 Birch Rd', '258 Willow Way', '369 Ash Ct'],
        'age': [25, 34, 19, 45, None, 28, 52, 41, 33, 29]
    })
    
    # Sample transactions data
    transactions_data = pd.DataFrame({
        'transaction_id': range(1, 21),
        'member_id': [1, 2, 3, 4, 5, 1, 2, 6, 7, 8, 9, 10, 3, 4, 5, 6, 7, 8, 9, 1],
        'isbn': ['978-0123456789', '978-0987654321', '978-0555666777', '978-0123456789', '978-0987654321'] * 4,
        'issue_date': pd.date_range('2024-01-01', periods=20, freq='3D'),
        'due_date': pd.date_range('2024-01-15', periods=20, freq='3D'),
        'return_date': [None if i % 4 == 0 else pd.Timestamp('2024-01-01') + pd.Timedelta(days=i*3+10) for i in range(20)],
        'status': ['issued', 'returned', 'returned', 'overdue', 'returned'] * 4,
        'fine_amount': [0.0, 0.0, 0.0, 5.50, 0.0] * 4
    })
    
    # Create data directory and save files
    os.makedirs('data/raw', exist_ok=True)
    
    books_data.to_csv('data/raw/books_import.csv', index=False)
    members_data.to_csv('data/raw/members_import.csv', index=False)
    transactions_data.to_csv('data/raw/transactions_import.csv', index=False)
    
    print("✅ Sample data files created:")
    print(f"  - books_import.csv: {len(books_data)} records")
    print(f"  - members_import.csv: {len(members_data)} records") 
    print(f"  - transactions_import.csv: {len(transactions_data)} records")

def create_pipeline_configurations():
    """Create default pipeline configurations"""
    
    # Configuration for library data processing pipeline
    library_pipeline_config = {
        "name": "library_data_processing",
        "description": "Daily library data processing and quality assurance",
        "config": {
            "stop_on_error": False,
            "max_retries": 3
        },
        "extractors": [
            {
                "name": "books_csv_extractor",
                "class": "CSVExtractor",
                "params": {
                    "file_path": "data/raw/books_import.csv"
                },
                "config": {
                    "encoding": "utf-8",
                    "header": 0
                }
            }
        ],
        "transformers": [
            {
                "name": "books_data_cleaner",
                "class": "DataCleaner",
                "params": {},
                "config": {
                    "auto_clean": True,
                    "cleaning_rules": [
                        {
                            "type": "remove_nulls",
                            "columns": ["isbn", "title"],
                            "threshold": 0.0
                        },
                        {
                            "type": "standardize_case",
                            "column": "genre",
                            "case_type": "title"
                        },
                        {
                            "type": "fill_missing",
                            "column": "price",
                            "strategy": "mean"
                        }
                    ]
                }
            },
            {
                "name": "books_transformer",
                "class": "LibraryDataTransformer",
                "params": {},
                "config": {
                    "data_type": "books"
                }
            }
        ],
        "loaders": [
            {
                "name": "books_staging_loader",
                "class": "StagingLoader",
                "params": {
                    "staging_path": "data/staging"
                },
                "config": {
                    "format": "parquet",
                    "add_metadata": True
                }
            },
            {
                "name": "books_csv_export",
                "class": "CSVLoader",
                "params": {
                    "file_path": "data/processed/books_cleaned.csv"
                },
                "config": {
                    "create_backup": True
                }
            }
        ]
    }
    
    # Save pipeline configuration
    os.makedirs('config', exist_ok=True)
    with open('config/pipeline_configs.json', 'w') as f:
        json.dump({
            "library_data_processing": library_pipeline_config
        }, f, indent=2, default=str)
    
    print("✅ Pipeline configurations created")

def setup_scheduler_infrastructure():
    """Set up scheduler infrastructure"""
    
    # Create scheduler config directory
    os.makedirs('schedulers', exist_ok=True)
    
    # Create default schedule configuration
    schedule_config = {
        "library_daily_etl": {
            "pipeline": "library_data_processing",
            "schedule": {
                "type": "daily",
                "time": "02:00"
            },
            "enabled": True,
            "notifications": {
                "on_failure": True,
                "on_success": False
            }
        },
        "data_quality_check": {
            "pipeline": "quality_validation",
            "schedule": {
                "type": "interval",
                "interval": 240  # Every 4 hours
            },
            "enabled": True
        }
    }
    
    with open('schedulers/schedule_config.json', 'w') as f:
        json.dump(schedule_config, f, indent=2)
    
    print("✅ Scheduler infrastructure set up")

def demo_etl_pipeline():
    """Demonstrate the ETL pipeline functionality"""
    print("\n🎬 Starting ETL Pipeline Demo...")
    
    # Initialize quality monitor
    monitor = DataQualityMonitor()
    
    # Create a simple ETL pipeline
    pipeline = ETLPipeline("demo_pipeline", {"stop_on_error": False})
    
    # Add components
    extractor = CSVExtractor(
        name="books_extractor",
        file_path="data/raw/books_import.csv"
    )
    
    transformer = DataCleaner(
        name="books_cleaner",
        config={
            "auto_clean": True,
            "cleaning_rules": [
                {"type": "remove_nulls", "columns": ["isbn"], "threshold": 0.0},
                {"type": "standardize_case", "column": "genre", "case_type": "title"}
            ]
        }
    )
    
    loader = CSVLoader(
        name="books_loader", 
        file_path="data/processed/books_demo_output.csv"
    )
    
    # Add quality validator
    quality_rules = [
        {"type": "not_null", "column": "isbn", "error_message": "ISBN cannot be null"},
        {"type": "not_null", "column": "title", "error_message": "Title cannot be null"},
        {"type": "unique", "column": "isbn", "error_message": "ISBN must be unique"},
        {"type": "range", "column": "publication_year", "min": 1800, "max": 2025}
    ]
    
    validator = DataQualityValidator(
        name="books_validator",
        rules=quality_rules,
        config={"strict_mode": False}
    )
    
    # Add components to pipeline
    pipeline.add_component(extractor)
    pipeline.add_component(transformer)
    pipeline.add_component(validator)
    pipeline.add_component(loader)
    
    # Execute pipeline
    print("\n⚡ Executing ETL pipeline...")
    results = pipeline.execute()
    
    # Display results
    print(f"\n📊 Pipeline Results:")
    print(f"  Status: {results['status']}")
    print(f"  Duration: {results['duration']:.2f} seconds")
    print(f"  Components: {results['successful_components']}/{results['total_components']} successful")
    
    # Read and analyze the processed data
    if os.path.exists("data/processed/books_demo_output.csv"):
        processed_data = pd.read_csv("data/processed/books_demo_output.csv")
        print(f"\n📈 Processed Data Summary:")
        print(f"  Records processed: {len(processed_data)}")
        print(f"  Columns: {list(processed_data.columns)}")
        
        # Run quality analysis
        print(f"\n🔍 Running quality analysis...")
        quality_metrics = monitor.analyze_data_quality(processed_data, "demo_pipeline", "books")
        
        # Display quality metrics
        passed_metrics = len([m for m in quality_metrics if m.status == "pass"])
        total_metrics = len(quality_metrics)
        print(f"  Quality checks: {passed_metrics}/{total_metrics} passed")
        
        # Show failed metrics
        failed_metrics = [m for m in quality_metrics if m.status == "fail"]
        if failed_metrics:
            print(f"\n⚠️  Quality Issues Found:")
            for metric in failed_metrics[:5]:  # Show first 5
                print(f"    - {metric.name}: {metric.message}")
    
    return results

def create_monitoring_dashboard_setup():
    """Set up monitoring dashboard configuration"""
    
    # Create monitoring configuration
    monitoring_config = {
        "quality_thresholds": {
            "completeness": 0.95,
            "accuracy": 0.98,
            "consistency": 0.95,
            "validity": 0.99,
            "uniqueness": 0.98
        },
        "alert_settings": {
            "email_notifications": False,
            "slack_webhook": None,
            "retention_days": 30
        },
        "dashboard_settings": {
            "refresh_interval": 300,  # 5 minutes
            "default_time_range": 24,  # 24 hours
            "auto_acknowledge_alerts": False
        }
    }
    
    os.makedirs('config', exist_ok=True)
    with open('config/monitoring_config.json', 'w') as f:
        json.dump(monitoring_config, f, indent=2)
    
    print("✅ Monitoring dashboard configuration created")

def run_complete_demo():
    """Run the complete ETL infrastructure demo"""
    
    print("🚀 Phase 4: Complete ETL Infrastructure Demo")
    print("=" * 60)
    
    # 1. Setup infrastructure
    monitor = setup_etl_infrastructure()
    
    # 2. Setup monitoring dashboard
    create_monitoring_dashboard_setup()
    
    # 3. Run ETL pipeline demo
    demo_results = demo_etl_pipeline()
    
    # 4. Generate quality report
    print("\n📋 Generating Quality Report...")
    quality_report = monitor.get_quality_report("demo_pipeline", days=1)
    
    print(f"\n📊 Quality Report Summary:")
    print(f"  Overall Quality Score: {quality_report['summary']['overall_quality_score']:.2%}")
    print(f"  Overall Health Score: {quality_report['summary']['overall_health_score']:.2%}")
    print(f"  Total Quality Checks: {quality_report['summary']['total_quality_checks']}")
    print(f"  Active Alerts: {quality_report['summary']['active_alerts']}")
    
    # 5. Show project structure
    print(f"\n📁 Project Structure Created:")
    print_project_structure()
    
    # 6. Usage instructions
    print_usage_instructions()
    
    return {
        "infrastructure_setup": "completed",
        "demo_results": demo_results,
        "quality_report": quality_report,
        "status": "success"
    }

def print_project_structure():
    """Print the created project structure"""
    structure = """
📁 ETL Infrastructure Structure:
├── 📁 data/
│   ├── 📁 raw/                    # Source data files
│   ├── 📁 processed/              # Cleaned and processed data
│   └── 📁 staging/                # Intermediate processing area
├── 📁 pipelines/
│   ├── 📄 etl_framework.py        # Core ETL framework
│   ├── 📁 extractors/
│   │   └── 📄 data_extractors.py  # Data extraction components
│   ├── 📁 transformers/
│   │   └── 📄 data_transformers.py # Data transformation components
│   └── 📁 loaders/
│       └── 📄 data_loaders.py     # Data loading components
├── 📁 schedulers/
│   └── 📄 pipeline_scheduler.py   # Pipeline scheduling system
├── 📁 monitoring/
│   └── 📄 quality_monitor.py      # Quality monitoring system
└── 📁 config/
    ├── 📄 pipeline_configs.json   # Pipeline configurations
    └── 📄 monitoring_config.json  # Monitoring settings
"""
    print(structure)

def print_usage_instructions():
    """Print usage instructions for the ETL infrastructure"""
    instructions = """
🎯 Phase 4 ETL Infrastructure - Usage Instructions:

1. 📊 Run ETL Pipelines:
   python setup_phase4_etl.py

2. 🔍 Monitor Data Quality:
   from monitoring.quality_monitor import DataQualityMonitor
   monitor = DataQualityMonitor()
   report = monitor.get_quality_report()

3. ⚙️ Create Custom Pipelines:
   from pipelines.etl_framework import ETLPipeline
   from pipelines.extractors.data_extractors import CSVExtractor
   # ... add components and execute

4. 📈 View Quality Metrics:
   Check monitoring/quality_metrics.db for detailed metrics

5. 🔔 Manage Alerts:
   monitor.get_alerts()  # View active alerts
   monitor.acknowledge_alert(alert_id)  # Acknowledge alerts

6. 📅 Schedule Automated Pipelines:
   from schedulers.pipeline_scheduler import PipelineScheduler
   scheduler = PipelineScheduler()
   scheduler.start_scheduler()

Key Features Implemented:
✅ Automated data extraction from multiple sources
✅ Data cleaning and transformation pipelines
✅ Quality validation and monitoring
✅ Automated scheduling and orchestration
✅ Comprehensive error handling and logging
✅ Data profiling and anomaly detection
✅ Alert system for quality issues
✅ Staging area for data processing
✅ Health scoring and metrics tracking
"""
    print(instructions)

if __name__ == "__main__":
    # Run the complete demo
    try:
        results = run_complete_demo()
        print(f"\n🎉 Phase 4 ETL Infrastructure Demo Completed Successfully!")
        print(f"📋 Check the generated files and monitoring data for details.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
