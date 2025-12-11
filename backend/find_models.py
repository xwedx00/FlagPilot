"""Query OpenRouter for stable (non-experimental) free models"""
import requests

response = requests.get('https://openrouter.ai/api/v1/models')
data = response.json()
free_models = [m for m in data.get('data', []) if ':free' in m.get('id', '')]

# Filter out experimental/flash models that tend to have stricter rate limits
good_models = []
for m in free_models:
    model_id = m.get('id', '')
    # Skip experimental and flash (often rate-limited)
    if 'exp' in model_id.lower() or '-exp:' in model_id:
        continue
    good_models.append(m)

sorted_models = sorted(good_models, key=lambda x: x.get('context_length', 0), reverse=True)

print("STABLE FREE MODELS (no experimental tag):")
print("=" * 60)
for m in sorted_models[:15]:
    mid = m['id']
    ctx = m.get('context_length', 0)
    desc = (m.get('description', '') or '')[:80]
    print(f"{mid}")
    print(f"  Context: {ctx:,} | {desc}...")
    print()
