"""
ML Model Training Pipeline
Trains Random Forest and other models for traffic prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
from datetime import datetime

def generate_training_data():
    """Generate synthetic training data based on traffic patterns"""
    np.random.seed(42)
    
    # Generate 10,000 samples
    n_samples = 10000
    
    data = {
        'hour': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'is_weekend': np.random.randint(0, 2, n_samples),
        'is_rush_hour': np.zeros(n_samples),
        'vehicle_count': np.random.randint(20, 400, n_samples),
        'avg_speed': np.random.randint(8, 65, n_samples),
        'density': np.random.randint(10, 100, n_samples),
        'congestion_level': []
    }
    
    # Mark rush hours
    for i in range(n_samples):
        if data['hour'][i] in [8, 9, 17, 18]:
            data['is_rush_hour'][i] = 1
    
    # Determine congestion level based on features
    for i in range(n_samples):
        if data['density'][i] > 70 or (data['vehicle_count'][i] > 250 and data['avg_speed'][i] < 20):
            data['congestion_level'].append('H')
        elif data['density'][i] > 40 or data['vehicle_count'][i] > 150:
            data['congestion_level'].append('M')
        else:
            data['congestion_level'].append('L')
    
    df = pd.DataFrame(data)
    return df

def train_models():
    """Train ML models for traffic prediction"""
    print("Starting ML model training...")
    
    # Generate training data
    df = generate_training_data()
    
    # Prepare features and labels
    features = ['hour', 'day_of_week', 'is_weekend', 'is_rush_hour', 
                'vehicle_count', 'avg_speed', 'density']
    X = df[features]
    y = df['congestion_level']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train Random Forest Classifier
    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    rf_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Random Forest Accuracy: {accuracy * 100:.2f}%")
    
    # Feature importance
    importance = dict(zip(features, rf_model.feature_importances_))
    print("Feature Importance:")
    for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {imp:.4f}")
    
    # Train Linear Regression for vehicle count prediction
    print("\nTraining Linear Regression for vehicle count...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, df.loc[X_train.index, 'vehicle_count'])
    
    lr_accuracy = lr_model.score(X_test, df.loc[X_test.index, 'vehicle_count'])
    print(f"Linear Regression R² Score: {lr_accuracy:.4f}")
    
    # Save models
    os.makedirs('/models', exist_ok=True)
    
    rf_path = '/models/random_forest_model.pkl'
    lr_path = '/models/linear_regression_model.pkl'
    
    joblib.dump(rf_model, rf_path)
    joblib.dump(lr_model, lr_path)
    
    print(f"\nModels saved:")
    print(f"  Random Forest: {rf_path}")
    print(f"  Linear Regression: {lr_path}")
    
    # Save model metadata
    metadata = {
        'trained_at': datetime.now().isoformat(),
        'accuracy': round(accuracy * 100, 2),
        'r2_score': round(lr_accuracy, 4),
        'feature_importance': {k: round(v, 4) for k, v in importance.items()},
        'training_samples': len(df),
        'features': features
    }
    
    import json
    with open('/models/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nTraining complete! Model accuracy: {accuracy * 100:.2f}%")
    return rf_model, lr_model

if __name__ == "__main__":
    train_models()
