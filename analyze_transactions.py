"""Analyze transactions_2025.csv with AWS Bedrock"""
import csv
import json
from src.screening_engine import ScreeningEngine
from src.database import Database

print("="*80)
print("TRANSACTION ANALYSIS WITH AWS BEDROCK LLM")
print("="*80)

# Initialize
engine = ScreeningEngine(use_mock=False, use_llm=True)
db = Database()

if not engine.bedrock_available:
    print("\n❌ AWS Bedrock not available!")
    exit(1)

print("\n✅ AWS Bedrock is ready\n")

# Read transactions
with open('sample_documents/transactions_2025.csv', 'r') as f:
    transactions = list(csv.DictReader(f))

print(f"📊 Analyzing {len(transactions)} transactions...\n")

results = []

for idx, txn in enumerate(transactions[:10], 1):  # First 10 for testing
    print(f"[{idx}/10] {txn['transaction_id']}: {txn['sender_name']} → {txn['receiver_name']}")
    print(f"    Amount: ${float(txn['amount']):,.2f}")
    
    # Analyze sender
    sender_risk = engine.screen_entity(
        name=txn['sender_name'],
        entity_type="individual",
        additional_context={"transaction_amount": float(txn['amount'])}
    )
    
    print(f"    Sender Risk: {sender_risk.final_risk_score:.1f}/100 ({sender_risk.risk_level})")
    
    # Analyze receiver  
    receiver_risk = engine.screen_entity(
        name=txn['receiver_name'],
        entity_type="organization",
        additional_context={"transaction_amount": float(txn['amount'])}
    )
    
    print(f"    Receiver Risk: {receiver_risk.final_risk_score:.1f}/100 ({receiver_risk.risk_level})")
    
    overall_risk = max(sender_risk.final_risk_score, receiver_risk.final_risk_score)
    print(f"    Overall: {overall_risk:.1f}/100\n")
    
    results.append({
        "transaction_id": txn['transaction_id'],
        "sender": txn['sender_name'],
        "receiver": txn['receiver_name'],
        "amount": float(txn['amount']),
        "sender_risk": sender_risk.final_risk_score,
        "receiver_risk": receiver_risk.final_risk_score,
        "overall_risk": overall_risk,
        "flags": sender_risk.flags + receiver_risk.flags
    })

# Save results
with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("="*80)
print(f"✅ Analysis complete! Results saved to analysis_results.json")
print("="*80)
