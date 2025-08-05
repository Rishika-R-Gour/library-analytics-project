#!/usr/bin/env python3
"""
Data Loading Components
Handles data loading to various destinations for the library analytics system
"""

import pandas as pd
import sqlite3
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import csv
from pipelines.etl_framework import DataLoader, ETLPipelineError

class DatabaseLoader(DataLoader):
    """Load data to database"""
    
    def __init__(self, name: str, db_path: str, table_name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.db_path = db_path
        self.table_name = table_name
        self.db_config = {
            'if_exists': config.get('if_exists', 'append'),  # 'fail', 'replace', 'append'
            'index': config.get('index', False),
            'method': config.get('method', None),
            'batch_size': config.get('batch_size', 1000),
            'create_indexes': config.get('create_indexes', []),
            'primary_key': config.get('primary_key', None)
        }
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to database table"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Load data to table
            data.to_sql(
                name=self.table_name,
                con=conn,
                if_exists=self.db_config['if_exists'],
                index=self.db_config['index'],
                method=self.db_config['method'],
                chunksize=self.db_config['batch_size']
            )
            
            # Create indexes if specified
            for index_config in self.db_config['create_indexes']:
                self._create_index(conn, index_config)
            
            # Set primary key if specified
            if self.db_config['primary_key']:
                self._set_primary_key(conn, self.db_config['primary_key'])
            
            conn.close()
            
            self.logger.info(f"Successfully loaded {len(data)} rows to table '{self.table_name}'")
            return True
            
        except Exception as e:
            raise ETLPipelineError(f"Failed to load data to database: {e}")
    
    def _create_index(self, conn: sqlite3.Connection, index_config: Dict[str, Any]):
        """Create database index"""
        try:
            index_name = index_config['name']
            columns = index_config['columns']
            unique = index_config.get('unique', False)
            
            unique_clause = 'UNIQUE' if unique else ''
            columns_clause = ', '.join(columns)
            
            query = f"CREATE {unique_clause} INDEX IF NOT EXISTS {index_name} ON {self.table_name} ({columns_clause})"
            conn.execute(query)
            conn.commit()
            
            self.logger.info(f"Created index '{index_name}' on table '{self.table_name}'")
            
        except Exception as e:
            self.logger.warning(f"Failed to create index '{index_name}': {e}")
    
    def _set_primary_key(self, conn: sqlite3.Connection, primary_key: str):
        """Set primary key (for new tables)"""
        try:
            # Note: SQLite doesn't support adding primary key to existing table
            # This would need to be handled during table creation
            self.logger.info(f"Primary key '{primary_key}' should be set during table creation")
            
        except Exception as e:
            self.logger.warning(f"Failed to set primary key: {e}")

class CSVLoader(DataLoader):
    """Load data to CSV file"""
    
    def __init__(self, name: str, file_path: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.file_path = file_path
        self.csv_config = {
            'index': config.get('index', False),
            'encoding': config.get('encoding', 'utf-8'),
            'delimiter': config.get('delimiter', ','),
            'mode': config.get('mode', 'w'),  # 'w' for write, 'a' for append
            'header': config.get('header', True),
            'create_backup': config.get('create_backup', True)
        }
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to CSV file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            # Create backup if file exists and backup is enabled
            if os.path.exists(self.file_path) and self.csv_config['create_backup']:
                backup_path = f"{self.file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.file_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # Write CSV file
            data.to_csv(
                self.file_path,
                index=self.csv_config['index'],
                encoding=self.csv_config['encoding'],
                sep=self.csv_config['delimiter'],
                mode=self.csv_config['mode'],
                header=self.csv_config['header']
            )
            
            self.logger.info(f"Successfully loaded {len(data)} rows to CSV: {self.file_path}")
            return True
            
        except Exception as e:
            raise ETLPipelineError(f"Failed to load data to CSV: {e}")

class ExcelLoader(DataLoader):
    """Load data to Excel file"""
    
    def __init__(self, name: str, file_path: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.file_path = file_path
        self.excel_config = {
            'sheet_name': config.get('sheet_name', 'Sheet1'),
            'index': config.get('index', False),
            'engine': config.get('engine', 'openpyxl'),
            'mode': config.get('mode', 'w'),  # 'w' for write, 'a' for append
            'if_sheet_exists': config.get('if_sheet_exists', 'replace'),
            'create_backup': config.get('create_backup', True)
        }
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to Excel file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            # Create backup if file exists and backup is enabled
            if os.path.exists(self.file_path) and self.excel_config['create_backup']:
                backup_path = f"{self.file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.file_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # Write Excel file
            with pd.ExcelWriter(
                self.file_path,
                engine=self.excel_config['engine'],
                mode=self.excel_config['mode'],
                if_sheet_exists=self.excel_config['if_sheet_exists']
            ) as writer:
                data.to_excel(
                    writer,
                    sheet_name=self.excel_config['sheet_name'],
                    index=self.excel_config['index']
                )
            
            self.logger.info(f"Successfully loaded {len(data)} rows to Excel: {self.file_path}")
            return True
            
        except Exception as e:
            raise ETLPipelineError(f"Failed to load data to Excel: {e}")

class JSONLoader(DataLoader):
    """Load data to JSON file"""
    
    def __init__(self, name: str, file_path: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.file_path = file_path
        self.json_config = {
            'orient': config.get('orient', 'records'),  # 'records', 'index', 'values', etc.
            'indent': config.get('indent', 2),
            'encoding': config.get('encoding', 'utf-8'),
            'create_backup': config.get('create_backup', True)
        }
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to JSON file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            # Create backup if file exists and backup is enabled
            if os.path.exists(self.file_path) and self.json_config['create_backup']:
                backup_path = f"{self.file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.file_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # Convert DataFrame to JSON
            json_data = data.to_json(
                orient=self.json_config['orient'],
                indent=self.json_config['indent']
            )
            
            # Write JSON file
            with open(self.file_path, 'w', encoding=self.json_config['encoding']) as f:
                f.write(json_data)
            
            self.logger.info(f"Successfully loaded {len(data)} rows to JSON: {self.file_path}")
            return True
            
        except Exception as e:
            raise ETLPipelineError(f"Failed to load data to JSON: {e}")

class ParquetLoader(DataLoader):
    """Load data to Parquet file"""
    
    def __init__(self, name: str, file_path: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.file_path = file_path
        self.parquet_config = {
            'compression': config.get('compression', 'snappy'),
            'index': config.get('index', False),
            'create_backup': config.get('create_backup', True)
        }
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to Parquet file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            # Create backup if file exists and backup is enabled
            if os.path.exists(self.file_path) and self.parquet_config['create_backup']:
                backup_path = f"{self.file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.file_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # Write Parquet file
            data.to_parquet(
                self.file_path,
                compression=self.parquet_config['compression'],
                index=self.parquet_config['index']
            )
            
            self.logger.info(f"Successfully loaded {len(data)} rows to Parquet: {self.file_path}")
            return True
            
        except Exception as e:
            raise ETLPipelineError(f"Failed to load data to Parquet: {e}")

class StagingLoader(DataLoader):
    """Load data to staging area with metadata"""
    
    def __init__(self, name: str, staging_path: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.staging_path = staging_path
        self.staging_config = {
            'format': config.get('format', 'parquet'),  # 'csv', 'parquet', 'json'
            'partition_by': config.get('partition_by', None),
            'retention_days': config.get('retention_days', 30),
            'add_metadata': config.get('add_metadata', True)
        }
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to staging area"""
        try:
            # Create staging directory
            os.makedirs(self.staging_path, exist_ok=True)
            
            # Add metadata if enabled
            if self.staging_config['add_metadata']:
                data = self._add_staging_metadata(data)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_extension = self.staging_config['format']
            filename = f"staged_data_{timestamp}.{file_extension}"
            file_path = os.path.join(self.staging_path, filename)
            
            # Partition data if specified
            if self.staging_config['partition_by']:
                self._partition_and_save(data, file_path)
            else:
                self._save_data(data, file_path)
            
            # Create metadata file
            self._create_metadata_file(data, file_path, timestamp)
            
            # Clean old files based on retention policy
            self._cleanup_old_files()
            
            self.logger.info(f"Successfully staged {len(data)} rows to: {file_path}")
            return True
            
        except Exception as e:
            raise ETLPipelineError(f"Failed to load data to staging: {e}")
    
    def _add_staging_metadata(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add staging metadata to data"""
        df = data.copy()
        df['_staged_at'] = datetime.now()
        df['_staging_id'] = f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        df['_record_count'] = len(df)
        return df
    
    def _partition_and_save(self, data: pd.DataFrame, base_path: str):
        """Partition data and save to multiple files"""
        partition_column = self.staging_config['partition_by']
        
        if partition_column not in data.columns:
            self.logger.warning(f"Partition column '{partition_column}' not found, saving without partitioning")
            self._save_data(data, base_path)
            return
        
        # Create partitioned directory structure
        for partition_value in data[partition_column].unique():
            partition_data = data[data[partition_column] == partition_value]
            
            # Create partition directory
            partition_dir = os.path.join(
                os.path.dirname(base_path),
                f"{partition_column}={partition_value}"
            )
            os.makedirs(partition_dir, exist_ok=True)
            
            # Save partition file
            partition_file = os.path.join(partition_dir, os.path.basename(base_path))
            self._save_data(partition_data, partition_file)
    
    def _save_data(self, data: pd.DataFrame, file_path: str):
        """Save data in specified format"""
        format_type = self.staging_config['format']
        
        if format_type == 'csv':
            data.to_csv(file_path, index=False)
        elif format_type == 'parquet':
            data.to_parquet(file_path, index=False)
        elif format_type == 'json':
            data.to_json(file_path, orient='records', indent=2)
        else:
            raise ETLPipelineError(f"Unsupported staging format: {format_type}")
    
    def _create_metadata_file(self, data: pd.DataFrame, file_path: str, timestamp: str):
        """Create metadata file for staged data"""
        metadata = {
            'staging_info': {
                'loader_name': self.name,
                'timestamp': timestamp,
                'file_path': file_path,
                'format': self.staging_config['format']
            },
            'data_profile': {
                'row_count': len(data),
                'column_count': len(data.columns),
                'columns': list(data.columns),
                'dtypes': data.dtypes.astype(str).to_dict(),
                'null_counts': data.isnull().sum().to_dict(),
                'memory_usage_mb': data.memory_usage(deep=True).sum() / 1024 / 1024
            },
            'quality_metrics': {
                'completeness': (data.size - data.isnull().sum().sum()) / data.size if data.size > 0 else 0,
                'duplicate_rows': data.duplicated().sum(),
                'unique_values': {col: data[col].nunique() for col in data.columns}
            }
        }
        
        metadata_file = f"{file_path}.metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def _cleanup_old_files(self):
        """Clean up old staged files based on retention policy"""
        try:
            retention_days = self.staging_config['retention_days']
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for file_path in Path(self.staging_path).glob('*'):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        file_path.unlink()
                        self.logger.info(f"Cleaned up old file: {file_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old files: {e}")

class LibraryTableLoader(DataLoader):
    """Specialized loader for library system tables"""
    
    def __init__(self, name: str, db_path: str, table_type: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.db_path = db_path
        self.table_type = table_type
        self.table_configs = {
            'books': {
                'table_name': 'books_staging',
                'primary_key': 'id',
                'indexes': [
                    {'name': 'idx_books_isbn', 'columns': ['isbn'], 'unique': True},
                    {'name': 'idx_books_title', 'columns': ['title']},
                    {'name': 'idx_books_author', 'columns': ['author_id']},
                    {'name': 'idx_books_genre', 'columns': ['genre']}
                ]
            },
            'members': {
                'table_name': 'members_staging',
                'primary_key': 'id',
                'indexes': [
                    {'name': 'idx_members_email', 'columns': ['email'], 'unique': True},
                    {'name': 'idx_members_phone', 'columns': ['phone']},
                    {'name': 'idx_members_name', 'columns': ['name']}
                ]
            },
            'transactions': {
                'table_name': 'transactions_staging',
                'primary_key': 'id',
                'indexes': [
                    {'name': 'idx_trans_member', 'columns': ['member_id']},
                    {'name': 'idx_trans_book', 'columns': ['book_id']},
                    {'name': 'idx_trans_date', 'columns': ['issue_date']},
                    {'name': 'idx_trans_status', 'columns': ['status']}
                ]
            }
        }
    
    def load(self, data: pd.DataFrame) -> bool:
        """Load data to library system table"""
        try:
            table_config = self.table_configs.get(self.table_type)
            if not table_config:
                raise ETLPipelineError(f"Unknown table type: {self.table_type}")
            
            table_name = table_config['table_name']
            
            # Prepare data for library system
            prepared_data = self._prepare_library_data(data)
            
            # Load to database
            conn = sqlite3.connect(self.db_path)
            
            # Create staging table if not exists
            self._create_staging_table(conn, table_name, prepared_data)
            
            # Load data
            prepared_data.to_sql(
                name=table_name,
                con=conn,
                if_exists='replace',
                index=False
            )
            
            # Create indexes
            for index_config in table_config['indexes']:
                self._create_index(conn, table_name, index_config)
            
            conn.close()
            
            self.logger.info(f"Successfully loaded {len(prepared_data)} rows to {table_name}")
            return True
            
        except Exception as e:
            raise ETLPipelineError(f"Failed to load library data: {e}")
    
    def _prepare_library_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for library system loading"""
        df = data.copy()
        
        # Add common fields
        df['created_at'] = datetime.now()
        df['updated_at'] = datetime.now()
        df['is_active'] = True
        
        # Table-specific preparations
        if self.table_type == 'books':
            df = self._prepare_books_data(df)
        elif self.table_type == 'members':
            df = self._prepare_members_data(df)
        elif self.table_type == 'transactions':
            df = self._prepare_transactions_data(df)
        
        return df
    
    def _prepare_books_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare books data"""
        # Ensure required columns exist
        required_columns = ['title', 'isbn', 'author_id', 'genre', 'publication_year']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Set default values
        df['status'] = df.get('status', 'available')
        df['copies_available'] = df.get('copies_available', 1)
        df['total_copies'] = df.get('total_copies', 1)
        
        return df
    
    def _prepare_members_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare members data"""
        # Ensure required columns exist
        required_columns = ['name', 'email', 'phone', 'address']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Set default values
        df['membership_type'] = df.get('membership_type', 'regular')
        df['join_date'] = pd.to_datetime(df.get('join_date', datetime.now()))
        df['status'] = df.get('status', 'active')
        
        return df
    
    def _prepare_transactions_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare transactions data"""
        # Ensure required columns exist
        required_columns = ['member_id', 'book_id', 'issue_date']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Set default values
        df['status'] = df.get('status', 'issued')
        df['due_date'] = pd.to_datetime(df.get('due_date', 
                                               pd.to_datetime(df['issue_date']) + pd.Timedelta(days=14)))
        
        return df
    
    def _create_staging_table(self, conn: sqlite3.Connection, table_name: str, data: pd.DataFrame):
        """Create staging table if not exists"""
        try:
            # Get column definitions
            columns_def = []
            for col in data.columns:
                dtype = data[col].dtype
                
                if 'int' in str(dtype):
                    sql_type = 'INTEGER'
                elif 'float' in str(dtype):
                    sql_type = 'REAL'
                elif 'datetime' in str(dtype):
                    sql_type = 'TIMESTAMP'
                elif 'bool' in str(dtype):
                    sql_type = 'BOOLEAN'
                else:
                    sql_type = 'TEXT'
                
                columns_def.append(f"{col} {sql_type}")
            
            # Create table
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns_def)}
            )
            """
            
            conn.execute(create_table_sql)
            conn.commit()
            
        except Exception as e:
            self.logger.warning(f"Failed to create staging table: {e}")
    
    def _create_index(self, conn: sqlite3.Connection, table_name: str, index_config: Dict[str, Any]):
        """Create database index"""
        try:
            index_name = index_config['name']
            columns = index_config['columns']
            unique = index_config.get('unique', False)
            
            unique_clause = 'UNIQUE' if unique else ''
            columns_clause = ', '.join(columns)
            
            query = f"CREATE {unique_clause} INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_clause})"
            conn.execute(query)
            conn.commit()
            
        except Exception as e:
            self.logger.warning(f"Failed to create index '{index_name}': {e}")

# Predefined loader configurations
LOADER_CONFIGS = {
    'library_books_db': {
        'class': LibraryTableLoader,
        'config': {
            'table_type': 'books'
        }
    },
    'library_members_db': {
        'class': LibraryTableLoader,
        'config': {
            'table_type': 'members'
        }
    },
    'library_transactions_db': {
        'class': LibraryTableLoader,
        'config': {
            'table_type': 'transactions'
        }
    },
    'csv_export': {
        'class': CSVLoader,
        'config': {
            'encoding': 'utf-8',
            'create_backup': True
        }
    },
    'staging_area': {
        'class': StagingLoader,
        'config': {
            'format': 'parquet',
            'retention_days': 30,
            'add_metadata': True
        }
    }
}

if __name__ == "__main__":
    print("💾 Data Loading Components Ready")
    print("Available loaders:")
    for name, config in LOADER_CONFIGS.items():
        print(f"  - {name}: {config['class'].__name__}")
