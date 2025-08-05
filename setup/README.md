# Setup Directory

This directory contains setup utilities and configuration scripts for the Library Analytics Project.

## Setup Files
- `setup_simple.py` - Basic project setup
- `setup_phase*.py` - Phase-specific database setup
- `test_api_start.py` - API testing utilities
- `check_status.py` - System status checker
- `fix_requirements.py` - Dependency management

## Database Setup
- `setup_phase3_db.py` - Phase 3 database configuration
- `setup_phase4_etl.py` - ETL pipeline setup
- `setup_phase5_database.py` - Final database setup

## Usage
Run setup scripts from project root:
```bash
python setup/setup_simple.py
python setup/check_status.py
```
