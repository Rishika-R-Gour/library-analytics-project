#!/usr/bin/env python3
"""
Library Analytics Model Management Script

This script manages the ML model lifecycle for the library analytics system,
including loading, validation, deployment, and monitoring of models.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """Manage ML models for the library analytics system"""
    
    def __init__(self, models_root="/Users/rishikagour/library_analytics_project/models"):
        self.models_root = Path(models_root)
        self.production_path = self.models_root / "production"
        self.staging_path = self.models_root / "staging"
        self.archived_path = self.models_root / "archived"
        
    def list_models(self, environment="production"):
        """List all models in specified environment"""
        env_path = self.models_root / environment
        models = []
        
        for model_dir in env_path.iterdir():
            if model_dir.is_dir():
                metadata_file = model_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    model_file = model_dir / metadata.get('model_file', '')
                    models.append({
                        'name': metadata['model_name'],
                        'version': metadata['version'],
                        'algorithm': metadata['algorithm'],
                        'path': str(model_dir),
                        'model_exists': model_file.exists(),
                        'size_mb': round(model_file.stat().st_size / (1024*1024), 2) if model_file.exists() else 0
                    })
        
        return models
    
    def load_model(self, model_name, environment="production"):
        """Load a specific model"""
        models = self.list_models(environment)
        model_info = next((m for m in models if model_name.lower() in m['name'].lower()), None)
        
        if not model_info:
            raise ValueError(f"Model '{model_name}' not found in {environment}")
        
        model_path = Path(model_info['path'])
        metadata_file = model_path / "metadata.json"
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        model_file = model_path / metadata['model_file']
        model = joblib.load(model_file)
        
        logger.info(f"Loaded {metadata['model_name']} v{metadata['version']}")
        return model, metadata
    
    def validate_model(self, model_name, environment="production"):
        """Validate model performance and integrity"""
        try:
            model, metadata = self.load_model(model_name, environment)
            
            # Basic validation tests
            validation_results = {
                'model_loads': True,
                'has_predict_method': hasattr(model, 'predict'),
                'metadata_complete': all(key in metadata for key in ['model_name', 'version', 'algorithm']),
                'performance_metrics_exist': 'performance_metrics' in metadata
            }
            
            # Test prediction (if possible)
            try:
                if hasattr(model, 'predict'):
                    # Create dummy data for testing
                    n_features = len(metadata.get('features', [5]))  # Default to 5 if no features listed
                    test_data = np.random.rand(1, n_features)
                    prediction = model.predict(test_data)
                    validation_results['prediction_test'] = True
                else:
                    validation_results['prediction_test'] = False
            except Exception as e:
                validation_results['prediction_test'] = False
                validation_results['prediction_error'] = str(e)
            
            validation_results['overall_valid'] = all([
                validation_results['model_loads'],
                validation_results['has_predict_method'],
                validation_results['metadata_complete']
            ])
            
            return validation_results
            
        except Exception as e:
            return {'error': str(e), 'overall_valid': False}
    
    def get_model_performance_summary(self):
        """Get performance summary of all production models"""
        models = self.list_models("production")
        summary = []
        
        for model_info in models:
            try:
                metadata_file = Path(model_info['path']) / "metadata.json"
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                performance = metadata.get('performance_metrics', {})
                summary.append({
                    'model': metadata['model_name'],
                    'version': metadata['version'],
                    'algorithm': metadata['algorithm'],
                    'accuracy': performance.get('accuracy', 'N/A'),
                    'size_mb': model_info['size_mb'],
                    'created': metadata.get('created_date', 'Unknown')
                })
            except Exception as e:
                logger.error(f"Error reading metadata for {model_info['name']}: {e}")
        
        return summary
    
    def promote_model(self, model_name, from_env="staging", to_env="production"):
        """Promote model from staging to production"""
        # This would implement model promotion logic
        logger.info(f"Promoting {model_name} from {from_env} to {to_env}")
        # Implementation would copy model files and update metadata
        pass
    
    def archive_model(self, model_name, version=None):
        """Archive old model version"""
        # This would implement model archival logic
        logger.info(f"Archiving {model_name} version {version}")
        pass
    
    def predict_overdue(self, loan_data):
        """Predict overdue probability for loans"""
        try:
            model_path = self.production_path / "overdue_prediction" / "overdue_prediction_model.pkl"
            
            if not model_path.exists():
                raise FileNotFoundError("Overdue prediction model not found")
            
            # Load model
            model = joblib.load(model_path)
            
            # For demo purposes, return mock predictions
            # In production, you would process the actual loan_data
            predictions = []
            
            if isinstance(loan_data, list):
                for i, loan in enumerate(loan_data):
                    probability = np.random.uniform(0.1, 0.9)  # Mock prediction
                    predictions.append({
                        'loan_id': loan.get('loan_id', i),
                        'overdue_probability': round(probability, 3),
                        'risk_level': 'High' if probability > 0.7 else 'Medium' if probability > 0.4 else 'Low'
                    })
            else:
                probability = np.random.uniform(0.1, 0.9)  # Mock prediction
                predictions = [{
                    'loan_id': loan_data.get('loan_id', 1),
                    'overdue_probability': round(probability, 3),
                    'risk_level': 'High' if probability > 0.7 else 'Medium' if probability > 0.4 else 'Low'
                }]
            
            return predictions
            
        except Exception as e:
            logger.error(f"Overdue prediction error: {e}")
            raise
    
    def predict_churn(self, member_data):
        """Predict member churn probability"""
        try:
            model_path = self.production_path / "churn_prediction" / "churn_prediction_model.pkl"
            
            if not model_path.exists():
                raise FileNotFoundError("Churn prediction model not found")
            
            # Load model
            model = joblib.load(model_path)
            
            # For demo purposes, return mock predictions
            # In production, you would process the actual member_data
            predictions = []
            
            if isinstance(member_data, list):
                for i, member in enumerate(member_data):
                    probability = np.random.uniform(0.05, 0.8)  # Mock prediction
                    predictions.append({
                        'member_id': member.get('member_id', i),
                        'churn_probability': round(probability, 3),
                        'risk_level': 'High' if probability > 0.6 else 'Medium' if probability > 0.3 else 'Low',
                        'retention_score': round(1 - probability, 3)
                    })
            else:
                probability = np.random.uniform(0.05, 0.8)  # Mock prediction
                predictions = [{
                    'member_id': member_data.get('member_id', 1),
                    'churn_probability': round(probability, 3),
                    'risk_level': 'High' if probability > 0.6 else 'Medium' if probability > 0.3 else 'Low',
                    'retention_score': round(1 - probability, 3)
                }]
            
            return predictions
            
        except Exception as e:
            logger.error(f"Churn prediction error: {e}")
            raise
    
    def get_recommendations(self, member_id, limit=5):
        """Get book recommendations for a member"""
        try:
            model_path = self.production_path / "recommendation_engine" / "recommendation_model.pkl"
            
            if not model_path.exists():
                raise FileNotFoundError("Recommendation model not found")
            
            # For demo purposes, return mock recommendations
            # In production, you would use the actual recommendation model
            
            genres = ['Fiction', 'Mystery', 'Science Fiction', 'Romance', 'Biography', 'History', 'Technology']
            authors = ['Jane Austen', 'Agatha Christie', 'Isaac Asimov', 'Stephen King', 'J.K. Rowling']
            
            recommendations = []
            for i in range(limit):
                score = np.random.uniform(0.6, 0.95)
                recommendations.append({
                    'book_id': np.random.randint(1, 500),
                    'title': f"Recommended Book {i+1}",
                    'author': np.random.choice(authors),
                    'genre': np.random.choice(genres),
                    'recommendation_score': round(score, 3),
                    'reason': f"Based on your reading history in {np.random.choice(genres)}"
                })
            
            # Sort by score
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations error: {e}")
            raise
    
    def get_models_status(self):
        """Get status of all production models"""
        models = self.list_models()
        
        status = {
            'total_models': len(models),
            'loaded_models': len([m for m in models if m['model_exists']]),
            'models': []
        }
        
        for model in models:
            model_status = {
                'name': model['name'],
                'version': model['version'],
                'algorithm': model['algorithm'],
                'status': 'loaded' if model['model_exists'] else 'missing',
                'size_mb': model['size_mb'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            status['models'].append(model_status)
        
        return status

def main():
    """Main function for command-line usage"""
    manager = ModelManager()
    
    print("🤖 **LIBRARY ANALYTICS MODEL MANAGEMENT**")
    print("=" * 45)
    
    # List all production models
    print("\n📊 **PRODUCTION MODELS:**")
    models = manager.list_models("production")
    for model in models:
        status = "✅" if model['model_exists'] else "❌"
        print(f"  {status} {model['name']} v{model['version']} ({model['size_mb']} MB)")
    
    # Validate all models
    print("\n🔍 **MODEL VALIDATION:**")
    for model in models:
        validation = manager.validate_model(model['name'])
        status = "✅" if validation.get('overall_valid', False) else "❌"
        print(f"  {status} {model['name']}: {'Valid' if validation.get('overall_valid') else 'Issues found'}")
    
    # Performance summary
    print("\n📈 **PERFORMANCE SUMMARY:**")
    summary = manager.get_model_performance_summary()
    for model in summary:
        accuracy = f"{model['accuracy']:.1%}" if isinstance(model['accuracy'], float) else model['accuracy']
        print(f"  • {model['model']}: {accuracy} accuracy ({model['algorithm']})")

if __name__ == "__main__":
    main()
