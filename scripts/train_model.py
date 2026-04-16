 
"""Script to train the fraud detection model."""
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from imblearn.over_sampling import SMOTE

def train_model():
    # Load data
    df = pd.read_csv('data/raw/creditcard.csv')
    
    # Add features
    df['transaction_hour'] = (df['Time'] / 3600) % 24
    df['is_night'] = ((df['transaction_hour'] >= 22) | (df['transaction_hour'] <= 5)).astype(int)
    df['is_small_amount'] = (df['Amount'] < 100).astype(int)
    df['is_round_amount'] = (df['Amount'] % 100 == 0).astype(int)
    
    # Prepare features
    feature_cols = [f'V{i}' for i in range(1, 29)] + ['Amount', 'Time'] + ['is_night', 'is_small_amount', 'is_round_amount']
    X = df[feature_cols]
    y = df['Class']
    
    # Scale
    scaler = StandardScaler()
    X[['Amount', 'Time']] = scaler.fit_transform(X[['Amount', 'Time']])
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    # SMOTE
    smote = SMOTE(random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)
    
    # Train
    model = xgb.XGBClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    
    # Save
    joblib.dump(model, 'models/fraud_pipeline.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')
    joblib.dump(list(X.columns), 'models/feature_names.joblib')
    
    print("✅ Model training complete!")

if __name__ == "__main__":
    train_model()