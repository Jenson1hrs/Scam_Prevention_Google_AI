#"""Script to download the Credit Card Fraud Detection dataset."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.settings import RAW_DATA_DIR

def download_data():
    """Instructions to download the dataset."""
    print("=" * 50)
    print("CREDIT CARD FRAUD DATASET DOWNLOAD")
    print("=" * 50)
    print()
    print("⚠️  You need to download the dataset manually:")
    print()
    print("1. Go to: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")
    print("2. Sign in to Kaggle (free account)")
    print("3. Click 'Download'")
    print(f"4. Save 'creditcard.csv' to:")
    print(f"   {RAW_DATA_DIR}\\creditcard.csv")
    print()
    print("=" * 50)
    print("Dataset Info:")
    print("- 284,807 transactions")
    print("- 492 fraud cases (0.172%)")
    print("- Features: V1-V28 (PCA), Time, Amount, Class")
    print("=" * 50)

def verify_data():
    """Check if dataset exists."""
    file_path = RAW_DATA_DIR / "creditcard.csv"
    
    if file_path.exists():
        import pandas as pd
        df = pd.read_csv(file_path)
        print(f"✅ Dataset found!")
        print(f"   Shape: {df.shape}")
        print(f"   Fraud cases: {df['Class'].sum()} ({df['Class'].mean()*100:.3f}%)")
        return True
    else:
        print(f"❌ Dataset not found at: {file_path}")
        return False

if __name__ == "__main__":
    download_data()
    
    print()
    print("Checking if dataset exists...")
    verify_data()