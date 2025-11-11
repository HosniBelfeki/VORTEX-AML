"""
Test script for AML Intelligence System
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        result = response.json()
        print(f"✓ Health check: {result['status']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_manual_analysis():
    """Test manual entity screening"""
    
    test_cases = [
        {"entity_name": "John Smith", "entity_type": "individual"},
        {"entity_name": "Vladimir Putin", "entity_type": "individual"},
        {"entity_name": "Bernie Madoff", "entity_type": "individual"},
        {"entity_name": "Joe Biden", "entity_type": "individual"}
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/analyze/manual",
                json=test_case
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"\n✓ Manual Analysis: {test_case['entity_name']}")
            print(f"  Risk Score: {result['risk_score']:.1f}/100")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Flags: {', '.join(result['flags']) if result['flags'] else 'None'}")
            print(f"  Processing Time: {result.get('processing_time_ms', 0)}ms")
            
            results.append(result)
            
        except Exception as e:
            print(f"✗ Manual analysis failed for {test_case['entity_name']}: {e}")
    
    return results

def test_dashboard():
    """Test dashboard statistics"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/stats")
        response.raise_for_status()
        stats = response.json()
        
        print(f"\n✓ Dashboard Stats:")
        print(f"  Total Analyses: {stats['total_analyses']}")
        print(f"  High Risk: {stats['high_risk_count']}")
        print(f"  Critical: {stats['critical_count']}")
        print(f"  Average Risk Score: {stats['average_risk_score']:.1f}")
        
        return stats
        
    except Exception as e:
        print(f"✗ Dashboard test failed: {e}")
        return None

def test_sar_generation():
    """Test SAR generation for critical risk cases"""
    
    # First, create a critical risk analysis
    critical_entity = {"entity_name": "Vladimir Putin", "entity_type": "individual"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze/manual",
            json=critical_entity
        )
        response.raise_for_status()
        analysis = response.json()
        
        if analysis['risk_level'] == 'CRITICAL':
            # Try to generate SAR
            sar_response = requests.post(
                f"{BASE_URL}/sars/generate",
                params={"analysis_id": analysis['analysis_id']}
            )
            sar_response.raise_for_status()
            sar = sar_response.json()
            
            print(f"\n✓ SAR Generation:")
            print(f"  Analysis ID: {analysis['analysis_id']}")
            print(f"  Ready to Submit: {sar['ready_to_submit']}")
            print(f"  Recipient: {sar['recipient']}")
            print(f"  SAR Preview: {sar['sar_filing'][:200]}...")
            
            return sar
        else:
            print(f"\n⚠ Entity {critical_entity['entity_name']} not critical risk, cannot test SAR generation")
            
    except Exception as e:
        print(f"✗ SAR generation test failed: {e}")
        return None

def test_list_analyses():
    """Test listing analyses"""
    try:
        response = requests.get(f"{BASE_URL}/analyses?limit=5")
        response.raise_for_status()
        result = response.json()
        
        print(f"\n✓ Recent Analyses:")
        print(f"  Total: {result['total']}")
        
        for i, analysis in enumerate(result['analyses'][:3], 1):
            entity_name = analysis.get('entity_name', 'Unknown')
            risk_level = analysis.get('risk_level', 'Unknown')
            print(f"  {i}. {entity_name} - {risk_level}")
        
        return result
        
    except Exception as e:
        print(f"✗ List analyses test failed: {e}")
        return None

def run_comprehensive_test():
    """Run all tests in sequence"""
    
    print("=" * 60)
    print("AML Intelligence System - Comprehensive Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n✗ System not healthy, aborting tests")
        return False
    
    # Test 2: Manual analysis
    print("\n" + "-" * 40)
    print("Testing Manual Entity Screening")
    print("-" * 40)
    analysis_results = test_manual_analysis()
    
    # Test 3: Dashboard
    print("\n" + "-" * 40)
    print("Testing Dashboard")
    print("-" * 40)
    dashboard_stats = test_dashboard()
    
    # Test 4: List analyses
    print("\n" + "-" * 40)
    print("Testing Analysis Listing")
    print("-" * 40)
    list_result = test_list_analyses()
    
    # Test 5: SAR generation
    print("\n" + "-" * 40)
    print("Testing SAR Generation")
    print("-" * 40)
    sar_result = test_sar_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    if test_health(): tests_passed += 1
    if analysis_results: tests_passed += 1
    if dashboard_stats: tests_passed += 1
    if list_result: tests_passed += 1
    if sar_result: tests_passed += 1
    
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! System is working correctly.")
    else:
        print(f"⚠ {total_tests - tests_passed} test(s) failed.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    success = run_comprehensive_test()
    
    if success:
        print("\n🎉 AML Intelligence System is ready for demo!")
    else:
        print("\n❌ Some tests failed. Check the server logs.")