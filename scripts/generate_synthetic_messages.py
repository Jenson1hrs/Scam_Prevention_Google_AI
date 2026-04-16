"""Generate synthetic Malaysian scam messages for testing."""
import json

scam_messages = [
    "Your Maybank account has been locked. Click here to verify: http://fake.com",
    "You won RM10,000! Send RM500 to claim your prize.",
    "Urgent: Your credit card was used for RM5,000. Call 0123456789 now.",
    "I'm from LHDN. You owe taxes. Pay immediately to avoid arrest.",
    "Your Touch 'n Go eWallet has expired. Update here: http://fake-link.com"
]

# Save to synthetic folder
with open('data/synthetic/malaysian_scam_messages.json', 'w') as f:
    json.dump(scam_messages, f, indent=2)

print(f"✅ Saved {len(scam_messages)} scam messages")