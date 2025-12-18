
import os
from ragflow_sdk import RAGFlow

api_key = os.environ.get("RAGFLOW_API_KEY", "ragflow-CM2ywnXT2ZcVeHxfeoTLW3yJgXVcOYsm1Q3XjKnxyLU")
base_url = "http://ragflow:80"
model = "openai/text-embedding-3-small@OpenAI"

client = RAGFlow(api_key=api_key, base_url=base_url)

def fix_datasets():
    print(f"Fixing RAGFlow datasets to use model: {model}")
    datasets = client.list_datasets()
    for ds in datasets:
        print(f"Updating dataset '{ds.name}' ({ds.id})...")
        try:
            ds.update({"embedding_model": model})
            print("  Success")
        except Exception as e:
            print(f"  Failed: {e}")

if __name__ == "__main__":
    fix_datasets()
