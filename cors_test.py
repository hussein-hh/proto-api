import requests
import sys
import json
from urllib.parse import urljoin

def test_cors_headers(url):
    """
    Test if a URL returns proper CORS headers in response to OPTIONS and GET requests.
    Also checks for duplicate headers which can cause browser issues.
    """
    print(f"Testing CORS headers for: {url}")
    
    # Test OPTIONS request (preflight)
    headers = {
        'Origin': 'https://proto-ux.netlify.app',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Authorization,Content-Type'
    }
    
    try:
        options_response = requests.options(url, headers=headers, timeout=10)
        print("\nOPTIONS Request:")
        print(f"Status Code: {options_response.status_code}")
        
        # Get all response headers (including duplicates)
        response_headers = options_response.raw.headers.items()
        
        # Track duplicates
        header_counts = {}
        cors_headers = {}
        
        print("Headers:")
        for name, value in response_headers:
            name_lower = name.lower()
            if name_lower.startswith('access-control'):
                print(f"  {name}: {value}")
                
                # Track occurrences for duplicate detection
                if name_lower not in header_counts:
                    header_counts[name_lower] = 1
                    cors_headers[name_lower] = [value]
                else:
                    header_counts[name_lower] += 1
                    cors_headers[name_lower].append(value)
        
        # Check for duplicates
        duplicates = {k: v for k, v in header_counts.items() if v > 1}
        if duplicates:
            print("\n⚠️ Duplicate CORS headers detected:")
            for header, count in duplicates.items():
                print(f"  {header}: {count} occurrences - Values: {cors_headers[header]}")
                print("  This will cause browsers to reject the CORS headers!")
        
        # Check if key CORS headers are present
        has_allow_origin = 'access-control-allow-origin' in cors_headers
        has_allow_methods = 'access-control-allow-methods' in cors_headers
        
        if has_allow_origin and has_allow_methods and not duplicates:
            print("✅ OPTIONS request has proper CORS headers")
        else:
            if not has_allow_origin:
                print("❌ Missing required header: Access-Control-Allow-Origin")
            if not has_allow_methods:
                print("❌ Missing required header: Access-Control-Allow-Methods")
            if duplicates:
                print("❌ Duplicate CORS headers must be fixed")
    except Exception as e:
        print(f"❌ OPTIONS request failed: {e}")
    
    # Test GET request
    headers = {
        'Origin': 'https://proto-ux.netlify.app',
        'Authorization': 'Bearer test-token'  # Include a dummy token
    }
    
    try:
        get_response = requests.get(url, headers=headers, timeout=10)
        print("\nGET Request:")
        print(f"Status Code: {get_response.status_code}")
        
        # Get all response headers (including duplicates)
        response_headers = get_response.raw.headers.items()
        
        # Track duplicates
        header_counts = {}
        cors_headers = {}
        
        print("Headers:")
        for name, value in response_headers:
            name_lower = name.lower()
            if name_lower.startswith('access-control'):
                print(f"  {name}: {value}")
                
                # Track occurrences for duplicate detection
                if name_lower not in header_counts:
                    header_counts[name_lower] = 1
                    cors_headers[name_lower] = [value]
                else:
                    header_counts[name_lower] += 1
                    cors_headers[name_lower].append(value)
        
        # Check for duplicates
        duplicates = {k: v for k, v in header_counts.items() if v > 1}
        if duplicates:
            print("\n⚠️ Duplicate CORS headers detected:")
            for header, count in duplicates.items():
                print(f"  {header}: {count} occurrences - Values: {cors_headers[header]}")
                print("  This will cause browsers to reject the CORS headers!")
        
        # Check if key CORS headers are present
        has_allow_origin = 'access-control-allow-origin' in cors_headers
        
        if has_allow_origin and not duplicates:
            print("✅ GET request has proper CORS headers")
        else:
            if not has_allow_origin:
                print("❌ Missing required header: Access-Control-Allow-Origin")
            if duplicates:
                print("❌ Duplicate CORS headers must be fixed")
                
        # Try to get response body for error details
        if get_response.status_code >= 400:
            try:
                body = get_response.json()
                print("\nResponse Body:")
                print(json.dumps(body, indent=2))
            except:
                print("\nResponse Body: Could not parse JSON")
                print(get_response.text[:200] + "..." if len(get_response.text) > 200 else get_response.text)
                
    except Exception as e:
        print(f"❌ GET request failed: {e}")

def test_all_endpoints():
    """Test both role-model and business endpoints"""
    base_url = "https://proto-api-kg9r.onrender.com"
    
    # Test business endpoint
    business_url = urljoin(base_url, "/toolkit/web-metrics/business/?page_id=54")
    print("=" * 80)
    print(f"TESTING BUSINESS ENDPOINT")
    print("=" * 80)
    test_cors_headers(business_url)
    
    # Test role-model endpoint
    role_model_url = urljoin(base_url, "/toolkit/web-metrics/role-model/?page_id=54")
    print("\n" + "=" * 80)
    print(f"TESTING ROLE MODEL ENDPOINT")
    print("=" * 80)
    test_cors_headers(role_model_url)

if __name__ == "__main__":
    # If an argument is provided, use it as the URL to test
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        test_cors_headers(test_url)
    else:
        # Test both endpoints
        test_all_endpoints()
    
    print("\nRun this script after deploying the changes to verify if CORS is working correctly.") 