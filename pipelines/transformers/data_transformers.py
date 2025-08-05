#!/usr/bin/env python3
"""
Data Transformation Components
Handles data cleaning, validation, and enrichment for the library analytics system
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import hashlib
from pipelines.etl_framework import DataTransformer, ETLPipelineError

class DataCleaner(DataTransformer):
    """General data cleaning transformer"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.cleaning_rules = config.get('cleaning_rules', [])
        self.auto_clean = config.get('auto_clean', True)
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply data cleaning transformations"""
        df = data.copy()
        
        # Auto-cleaning if enabled
        if self.auto_clean:
            df = self._auto_clean(df)
        
        # Apply custom cleaning rules
        for rule in self.cleaning_rules:
            df = self._apply_cleaning_rule(df, rule)
        
        self.logger.info(f"Data cleaning completed: {len(data)} -> {len(df)} rows")
        return df
    
    def _auto_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply automatic cleaning operations"""
        original_rows = len(df)
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Trim whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].astype(str).str.strip()
            # Replace empty strings with NaN
            df[col] = df[col].replace('', np.nan)
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        cleaned_rows = len(df)
        self.logger.info(f"Auto-cleaning removed {original_rows - cleaned_rows} rows")
        
        return df
    
    def _apply_cleaning_rule(self, df: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """Apply a specific cleaning rule"""
        rule_type = rule['type']
        
        try:
            if rule_type == 'remove_nulls':
                columns = rule.get('columns', df.columns)
                threshold = rule.get('threshold', 0.0)  # 0 = any null, 1 = all null
                
                if threshold == 0:
                    df = df.dropna(subset=columns, how='any')
                elif threshold == 1:
                    df = df.dropna(subset=columns, how='all')
                else:
                    # Remove rows where more than threshold% of specified columns are null
                    null_ratio = df[columns].isnull().sum(axis=1) / len(columns)
                    df = df[null_ratio <= threshold]
            
            elif rule_type == 'standardize_case':
                column = rule['column']
                case_type = rule.get('case_type', 'title')
                
                if case_type == 'upper':
                    df[column] = df[column].str.upper()
                elif case_type == 'lower':
                    df[column] = df[column].str.lower()
                elif case_type == 'title':
                    df[column] = df[column].str.title()
                elif case_type == 'sentence':
                    df[column] = df[column].str.capitalize()
            
            elif rule_type == 'remove_special_chars':
                column = rule['column']
                pattern = rule.get('pattern', r'[^\w\s]')
                replacement = rule.get('replacement', '')
                
                df[column] = df[column].str.replace(pattern, replacement, regex=True)
            
            elif rule_type == 'standardize_phone':
                column = rule['column']
                df[column] = df[column].apply(self._standardize_phone)
            
            elif rule_type == 'standardize_email':
                column = rule['column']
                df[column] = df[column].str.lower().str.strip()
                # Validate email format
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                invalid_emails = ~df[column].str.match(email_pattern, na=False)
                df.loc[invalid_emails, column] = np.nan
            
            elif rule_type == 'fill_missing':
                column = rule['column']
                strategy = rule.get('strategy', 'mean')
                value = rule.get('value', None)
                
                if value is not None:
                    df[column] = df[column].fillna(value)
                elif strategy == 'mean':
                    df[column] = df[column].fillna(df[column].mean())
                elif strategy == 'median':
                    df[column] = df[column].fillna(df[column].median())
                elif strategy == 'mode':
                    df[column] = df[column].fillna(df[column].mode().iloc[0])
                elif strategy == 'forward_fill':
                    df[column] = df[column].fillna(method='ffill')
                elif strategy == 'backward_fill':
                    df[column] = df[column].fillna(method='bfill')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to apply cleaning rule {rule_type}: {e}")
            return df
    
    def _standardize_phone(self, phone: str) -> str:
        """Standardize phone number format"""
        if pd.isna(phone):
            return phone
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone))
        
        # Format based on length
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone  # Return original if can't standardize

class DataValidator(DataTransformer):
    """Data validation transformer"""
    
    def __init__(self, name: str, validation_rules: List[Dict[str, Any]], config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.validation_rules = validation_rules
        self.strict_mode = config.get('strict_mode', False)
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate data and optionally filter invalid records"""
        df = data.copy()
        df['_validation_errors'] = ''
        
        for rule in self.validation_rules:
            df = self._apply_validation_rule(df, rule)
        
        # Count validation errors
        invalid_rows = df['_validation_errors'] != ''
        invalid_count = invalid_rows.sum()
        
        if invalid_count > 0:
            self.logger.warning(f"Found {invalid_count} rows with validation errors")
            
            if self.strict_mode:
                # Remove invalid rows in strict mode
                df = df[~invalid_rows]
                self.logger.info(f"Removed {invalid_count} invalid rows (strict mode)")
            else:
                # Keep validation error column for reference
                pass
        
        # Clean up validation error column if no errors
        if '_validation_errors' in df.columns and df['_validation_errors'].eq('').all():
            df = df.drop('_validation_errors', axis=1)
        
        return df
    
    def _apply_validation_rule(self, df: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """Apply a validation rule"""
        rule_type = rule['type']
        column = rule.get('column')
        error_message = rule.get('error_message', f"Validation failed: {rule_type}")
        
        try:
            if rule_type == 'not_null':
                invalid_mask = df[column].isnull()
            
            elif rule_type == 'email_format':
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                invalid_mask = ~df[column].astype(str).str.match(email_pattern, na=False)
            
            elif rule_type == 'phone_format':
                phone_pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
                invalid_mask = ~df[column].astype(str).str.match(phone_pattern, na=False)
            
            elif rule_type == 'range':
                min_val = rule.get('min')
                max_val = rule.get('max')
                invalid_mask = pd.Series([False] * len(df))
                
                if min_val is not None:
                    invalid_mask |= df[column] < min_val
                if max_val is not None:
                    invalid_mask |= df[column] > max_val
            
            elif rule_type == 'length':
                min_length = rule.get('min_length', 0)
                max_length = rule.get('max_length', float('inf'))
                
                lengths = df[column].astype(str).str.len()
                invalid_mask = (lengths < min_length) | (lengths > max_length)
            
            elif rule_type == 'pattern':
                pattern = rule['pattern']
                invalid_mask = ~df[column].astype(str).str.match(pattern, na=False)
            
            elif rule_type == 'in_list':
                valid_values = rule['values']
                invalid_mask = ~df[column].isin(valid_values)
            
            elif rule_type == 'unique':
                invalid_mask = df.duplicated(subset=[column], keep=False)
            
            elif rule_type == 'date_format':
                date_format = rule.get('format', '%Y-%m-%d')
                try:
                    pd.to_datetime(df[column], format=date_format, errors='raise')
                    invalid_mask = pd.Series([False] * len(df))
                except:
                    invalid_mask = pd.Series([True] * len(df))
            
            else:
                self.logger.warning(f"Unknown validation rule type: {rule_type}")
                return df
            
            # Add error messages for invalid rows
            df.loc[invalid_mask, '_validation_errors'] += f"{error_message}; "
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to apply validation rule {rule_type}: {e}")
            return df

class DataEnricher(DataTransformer):
    """Data enrichment transformer"""
    
    def __init__(self, name: str, enrichment_rules: List[Dict[str, Any]], config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.enrichment_rules = enrichment_rules
        self.lookup_data = config.get('lookup_data', {})
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Enrich data with additional information"""
        df = data.copy()
        
        for rule in self.enrichment_rules:
            df = self._apply_enrichment_rule(df, rule)
        
        return df
    
    def _apply_enrichment_rule(self, df: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """Apply an enrichment rule"""
        rule_type = rule['type']
        
        try:
            if rule_type == 'add_timestamp':
                column_name = rule.get('column_name', 'processed_timestamp')
                df[column_name] = datetime.now()
            
            elif rule_type == 'add_row_id':
                column_name = rule.get('column_name', 'row_id')
                df[column_name] = range(1, len(df) + 1)
            
            elif rule_type == 'add_hash':
                source_columns = rule['source_columns']
                target_column = rule['target_column']
                
                # Create hash from specified columns
                df[target_column] = df[source_columns].apply(
                    lambda row: hashlib.md5(''.join(row.astype(str)).encode()).hexdigest(),
                    axis=1
                )
            
            elif rule_type == 'category_mapping':
                source_column = rule['source_column']
                target_column = rule['target_column']
                mapping = rule['mapping']
                default_value = rule.get('default_value', 'Other')
                
                df[target_column] = df[source_column].map(mapping).fillna(default_value)
            
            elif rule_type == 'calculate_age':
                birth_date_column = rule['birth_date_column']
                target_column = rule.get('target_column', 'age')
                reference_date = rule.get('reference_date', datetime.now())
                
                df[target_column] = (reference_date - pd.to_datetime(df[birth_date_column])).dt.days // 365
            
            elif rule_type == 'extract_date_parts':
                date_column = rule['date_column']
                parts = rule.get('parts', ['year', 'month', 'day'])
                
                date_series = pd.to_datetime(df[date_column])
                
                if 'year' in parts:
                    df[f"{date_column}_year"] = date_series.dt.year
                if 'month' in parts:
                    df[f"{date_column}_month"] = date_series.dt.month
                if 'day' in parts:
                    df[f"{date_column}_day"] = date_series.dt.day
                if 'weekday' in parts:
                    df[f"{date_column}_weekday"] = date_series.dt.dayofweek
                if 'quarter' in parts:
                    df[f"{date_column}_quarter"] = date_series.dt.quarter
            
            elif rule_type == 'lookup_enrichment':
                key_column = rule['key_column']
                lookup_table = rule['lookup_table']
                target_columns = rule['target_columns']
                
                # Merge with lookup data
                if lookup_table in self.lookup_data:
                    lookup_df = self.lookup_data[lookup_table]
                    df = df.merge(lookup_df[target_columns + [key_column]], 
                                on=key_column, how='left')
            
            elif rule_type == 'text_features':
                text_column = rule['text_column']
                features = rule.get('features', ['length', 'word_count'])
                
                if 'length' in features:
                    df[f"{text_column}_length"] = df[text_column].astype(str).str.len()
                if 'word_count' in features:
                    df[f"{text_column}_word_count"] = df[text_column].astype(str).str.split().str.len()
                if 'uppercase_count' in features:
                    df[f"{text_column}_uppercase_count"] = df[text_column].astype(str).str.count(r'[A-Z]')
                if 'digit_count' in features:
                    df[f"{text_column}_digit_count"] = df[text_column].astype(str).str.count(r'\d')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to apply enrichment rule {rule_type}: {e}")
            return df

class LibraryDataTransformer(DataTransformer):
    """Specialized transformer for library data"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.data_type = config.get('data_type', 'general')
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform library-specific data"""
        df = data.copy()
        
        if self.data_type == 'books':
            df = self._transform_books_data(df)
        elif self.data_type == 'members':
            df = self._transform_members_data(df)
        elif self.data_type == 'transactions':
            df = self._transform_transactions_data(df)
        else:
            df = self._transform_general_data(df)
        
        return df
    
    def _transform_books_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform books data"""
        # Standardize ISBN format
        if 'isbn' in df.columns:
            df['isbn'] = df['isbn'].astype(str).str.replace('-', '').str.replace(' ', '')
        
        # Standardize genre categories
        if 'genre' in df.columns:
            genre_mapping = {
                'sci-fi': 'Science Fiction',
                'scifi': 'Science Fiction',
                'mystery': 'Mystery',
                'thriller': 'Thriller',
                'romance': 'Romance',
                'fantasy': 'Fantasy',
                'non-fiction': 'Non-Fiction',
                'biography': 'Biography',
                'history': 'History',
                'science': 'Science',
                'technology': 'Technology'
            }
            df['genre'] = df['genre'].str.lower().map(genre_mapping).fillna(df['genre'])
        
        # Extract publication year from date
        if 'publication_date' in df.columns:
            df['publication_year'] = pd.to_datetime(df['publication_date'], errors='coerce').dt.year
        
        # Calculate book age
        if 'publication_year' in df.columns:
            current_year = datetime.now().year
            df['book_age_years'] = current_year - df['publication_year']
        
        # Standardize title case
        if 'title' in df.columns:
            df['title'] = df['title'].str.title()
        
        return df
    
    def _transform_members_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform members data"""
        # Standardize email format
        if 'email' in df.columns:
            df['email'] = df['email'].str.lower().str.strip()
        
        # Standardize phone numbers
        if 'phone' in df.columns:
            df['phone'] = df['phone'].apply(self._standardize_phone)
        
        # Calculate membership duration
        if 'join_date' in df.columns:
            join_dates = pd.to_datetime(df['join_date'], errors='coerce')
            df['membership_days'] = (datetime.now() - join_dates).dt.days
            df['membership_years'] = df['membership_days'] / 365.25
        
        # Categorize members by activity
        if 'total_transactions' in df.columns:
            df['member_category'] = pd.cut(
                df['total_transactions'],
                bins=[0, 5, 15, 30, float('inf')],
                labels=['New', 'Regular', 'Active', 'Power User']
            )
        
        return df
    
    def _transform_transactions_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform transactions data"""
        # Convert date columns
        date_columns = ['issue_date', 'return_date', 'due_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calculate loan duration
        if 'issue_date' in df.columns and 'return_date' in df.columns:
            df['loan_duration_days'] = (df['return_date'] - df['issue_date']).dt.days
        
        # Calculate overdue status
        if 'due_date' in df.columns and 'return_date' in df.columns:
            df['is_overdue'] = df['return_date'] > df['due_date']
            df['overdue_days'] = (df['return_date'] - df['due_date']).dt.days
            df['overdue_days'] = df['overdue_days'].where(df['overdue_days'] > 0, 0)
        
        # Extract time features
        if 'issue_date' in df.columns:
            df['issue_year'] = df['issue_date'].dt.year
            df['issue_month'] = df['issue_date'].dt.month
            df['issue_weekday'] = df['issue_date'].dt.dayofweek
            df['issue_quarter'] = df['issue_date'].dt.quarter
        
        # Categorize transaction status
        if 'status' in df.columns:
            status_mapping = {
                'issued': 'Active',
                'returned': 'Completed',
                'overdue': 'Overdue',
                'lost': 'Lost',
                'damaged': 'Damaged'
            }
            df['status_category'] = df['status'].str.lower().map(status_mapping).fillna(df['status'])
        
        return df
    
    def _transform_general_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply general transformations"""
        # Add processing metadata
        df['processed_at'] = datetime.now()
        df['data_source'] = self.name
        
        return df
    
    def _standardize_phone(self, phone: str) -> str:
        """Standardize phone number format"""
        if pd.isna(phone):
            return phone
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone))
        
        # Format based on length
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone  # Return original if can't standardize

# Predefined transformation configurations
TRANSFORMER_CONFIGS = {
    'library_books_cleaner': {
        'class': LibraryDataTransformer,
        'config': {
            'data_type': 'books'
        }
    },
    'library_members_cleaner': {
        'class': LibraryDataTransformer,
        'config': {
            'data_type': 'members'
        }
    },
    'library_transactions_cleaner': {
        'class': LibraryDataTransformer,
        'config': {
            'data_type': 'transactions'
        }
    },
    'general_data_cleaner': {
        'class': DataCleaner,
        'config': {
            'auto_clean': True,
            'cleaning_rules': [
                {'type': 'remove_nulls', 'threshold': 0.5},
                {'type': 'standardize_case', 'column': 'name', 'case_type': 'title'},
                {'type': 'standardize_email', 'column': 'email'},
                {'type': 'standardize_phone', 'column': 'phone'}
            ]
        }
    }
}

if __name__ == "__main__":
    print("🔄 Data Transformation Components Ready")
    print("Available transformers:")
    for name, config in TRANSFORMER_CONFIGS.items():
        print(f"  - {name}: {config['class'].__name__}")
