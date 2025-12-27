"""
Smart-Stack Feature Test Suite
==============================
Tests all new features: PostgresCheckpointer, Long-term Memory, LLM Router
"""

import os
import sys

def run_tests():
    print("=" * 50)
    print("SMART-STACK FEATURE TEST SUITE")
    print("=" * 50)
    
    results = {}
    
    # Test 1: PostgresCheckpointer
    print("\n[1] PostgresCheckpointer Test:")
    try:
        from lib.persistence import get_checkpointer
        cp = get_checkpointer()
        cp_type = type(cp).__name__
        is_postgres = cp_type == "PostgresSaver"
        print(f"    Type: {cp_type}")
        print(f"    Is Postgres: {is_postgres}")
        results["checkpointer"] = "PASS" if is_postgres else "WARN (using MemorySaver)"
    except Exception as e:
        print(f"    ERROR: {e}")
        results["checkpointer"] = f"FAIL: {e}"
    
    # Test 2: Long-term Memory Store
    print("\n[2] Long-term Memory Store Test:")
    try:
        from lib.persistence import get_long_term_memory
        ltm = get_long_term_memory()
        store_type = type(ltm.store).__name__
        is_persistent = ltm.is_persistent
        print(f"    Store Type: {store_type}")
        print(f"    Is Persistent: {is_persistent}")
        results["long_term_memory"] = "PASS" if is_persistent else "WARN (using InMemoryStore)"
    except Exception as e:
        print(f"    ERROR: {e}")
        results["long_term_memory"] = f"FAIL: {e}"
    
    # Test 3: Memory Operations
    print("\n[3] Memory Operations Test:")
    try:
        result = ltm.remember("test_user", "test_memory", {"data": "Hello from test!"})
        recalled = ltm.get_memory("test_user", "test_memory")
        print(f"    Remember: {result}")
        print(f"    Recall: {recalled}")
        results["memory_ops"] = "PASS" if result and recalled else "FAIL"
    except Exception as e:
        print(f"    ERROR: {e}")
        results["memory_ops"] = f"FAIL: {e}"
    
    # Test 4: LLM Router
    print("\n[4] LLM Router Test:")
    try:
        from agents.router import AGENT_REGISTRY, fallback_keyword_route
        num_agents = len(AGENT_REGISTRY)
        print(f"    Agents in Registry: {num_agents}")
        test_route = fallback_keyword_route("I need to analyze this contract")
        print(f"    Test Route (contract): {test_route}")
        results["llm_router"] = "PASS" if num_agents > 0 else "FAIL"
    except Exception as e:
        print(f"    ERROR: {e}")
        results["llm_router"] = f"FAIL: {e}"
    
    # Test 5: Environment Check
    print("\n[5] Environment Check:")
    db_url = os.environ.get("DATABASE_URL")
    openrouter = os.environ.get("OPENROUTER_API_KEY")
    langsmith = os.environ.get("LANGSMITH_API_KEY")
    redis = os.environ.get("REDIS_URL")
    print(f"    DATABASE_URL: {'Set' if db_url else 'Missing'}")
    print(f"    OPENROUTER_API_KEY: {'Set' if openrouter else 'Missing'}")
    print(f"    LANGSMITH_API_KEY: {'Set' if langsmith else 'Missing'}")
    print(f"    REDIS_URL: {'Set' if redis else 'Missing'}")
    
    # Test 6: Elasticsearch Connection
    print("\n[6] Elasticsearch Test:")
    try:
        from elasticsearch import Elasticsearch
        es_host = os.environ.get("ES_HOST", "es01")
        es = Elasticsearch([f"http://{es_host}:9200"])
        health = es.cluster.health()
        print(f"    Cluster: {health.get('cluster_name')}")
        print(f"    Status: {health.get('status')}")
        results["elasticsearch"] = "PASS" if health.get("status") in ["green", "yellow"] else "FAIL"
    except Exception as e:
        print(f"    ERROR: {e}")
        results["elasticsearch"] = f"FAIL: {e}"
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    for test, result in results.items():
        status_icon = "✓" if "PASS" in result else ("⚠" if "WARN" in result else "✗")
        print(f"    {status_icon} {test}: {result}")
    
    return results

if __name__ == "__main__":
    run_tests()
