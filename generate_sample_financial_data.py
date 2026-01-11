"""
Generate sample financial transaction dataset (PaySim-style)
This creates a small representative sample for testing and validation
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Number of sample transactions
N_TRANSACTIONS = 1000

# Generate timestamps (30 days simulated)
start_time = datetime(2024, 1, 1, 0, 0, 0)
timestamps = [start_time + timedelta(hours=i*0.72 + np.random.randint(-30, 30)/60) 
              for i in range(N_TRANSACTIONS)]

# Transaction types
transaction_types = np.random.choice(
    ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'CASH_IN'],
    size=N_TRANSACTIONS,
    p=[0.35, 0.25, 0.20, 0.15, 0.05]
)

# Generate account IDs
n_accounts = 200
account_ids_src = [f"C_{np.random.randint(1, n_accounts):06d}" 
                   for _ in range(N_TRANSACTIONS)]
account_ids_dst = [f"C_{np.random.randint(1, n_accounts):06d}" 
                   for _ in range(N_TRANSACTIONS)]

# Generate transaction amounts
# Log-normal distribution with different parameters for different types
amounts = []
for tx_type in transaction_types:
    if tx_type == 'PAYMENT':
        amount = np.random.lognormal(4.0, 1.5)
    elif tx_type == 'TRANSFER':
        amount = np.random.lognormal(6.0, 2.0)
    elif tx_type == 'CASH_OUT':
        amount = np.random.lognormal(5.5, 1.8)
    elif tx_type == 'DEBIT':
        amount = np.random.lognormal(4.5, 1.2)
    else:  # CASH_IN
        amount = np.random.lognormal(6.5, 2.5)
    amounts.append(round(amount, 2))

amounts = np.array(amounts)

# Generate balances
# Old balance for sender
old_balance_src = []
for i, amount in enumerate(amounts):
    # Ensure sender has enough balance
    min_balance = amount * 1.2
    old_balance_src.append(round(min_balance + np.random.exponential(5000), 2))

old_balance_src = np.array(old_balance_src)

# New balance for sender
new_balance_src = old_balance_src - amounts
new_balance_src = np.maximum(new_balance_src, 0)  # Can't be negative

# Balances for recipient
old_balance_dst = np.random.exponential(3000, N_TRANSACTIONS).round(2)
new_balance_dst = old_balance_dst + amounts

# Generate fraud labels (0.5% fraud rate, similar to real data)
is_fraud = np.random.random(N_TRANSACTIONS) < 0.013

# Fraud is more likely in large CASH_OUT and TRANSFER transactions
fraud_boost = (
    (transaction_types == 'CASH_OUT') | (transaction_types == 'TRANSFER')
) & (amounts > np.percentile(amounts, 90))
is_fraud = is_fraud | (fraud_boost & (np.random.random(N_TRANSACTIONS) < 0.05))

fraud_labels = is_fraud.astype(int)

# Generate fraud scores (higher for actual fraud)
fraud_scores = np.where(
    is_fraud,
    np.random.uniform(0.7, 1.0, N_TRANSACTIONS),
    np.random.uniform(0.0, 0.3, N_TRANSACTIONS)
)

# For fraud cases, balances might be suspicious
for i in range(N_TRANSACTIONS):
    if is_fraud[i]:
        # Fraudulent transactions often drain accounts
        if np.random.random() < 0.7:
            new_balance_src[i] = 0
            # And might show unusual patterns in destination
            if np.random.random() < 0.5:
                old_balance_dst[i] = 0

# Merchant flags (some transactions are to merchants)
is_merchant_dst = np.random.random(N_TRANSACTIONS) < 0.3
for i in range(N_TRANSACTIONS):
    if is_merchant_dst[i]:
        account_ids_dst[i] = f"M_{np.random.randint(1, 50):06d}"

# Step (time step in simulation)
steps = (np.array(range(N_TRANSACTIONS)) * 0.72).astype(int)

# Create DataFrame
df = pd.DataFrame({
    'timestamp': timestamps,
    'step': steps,
    'type': transaction_types,
    'amount': amounts,
    'nameOrig': account_ids_src,
    'oldbalanceOrg': old_balance_src,
    'newbalanceOrig': new_balance_src,
    'nameDest': account_ids_dst,
    'oldbalanceDest': old_balance_dst,
    'newbalanceDest': new_balance_dst,
    'isFraud': fraud_labels,
    'isFlaggedFraud': (fraud_labels & (amounts > 200000)).astype(int),
    'fraud_score': fraud_scores
})

# Add some derived features
df['balance_change_src'] = df['newbalanceOrig'] - df['oldbalanceOrg']
df['balance_change_dst'] = df['newbalanceDest'] - df['oldbalanceDest']
df['is_merchant'] = is_merchant_dst.astype(int)

# Calculate velocity features (simplified)
df['amount_ratio'] = df['amount'] / (df['oldbalanceOrg'] + 1)
df['balance_ratio_src'] = df['newbalanceOrig'] / (df['oldbalanceOrg'] + 1)

# Save to CSV
df.to_csv('sample_financial_data.csv', index=False)
print(f"Generated {N_TRANSACTIONS} financial transactions")
print(f"Fraud: {fraud_labels.sum()} ({100*fraud_labels.mean():.2f}%)")
print(f"\nTransaction type distribution:")
print(df['type'].value_counts())
print(f"\nAmount statistics:")
print(df['amount'].describe())
print(f"\nFraud by transaction type:")
print(df[df['isFraud']==1]['type'].value_counts())
print("\nSaved to: sample_financial_data.csv")
