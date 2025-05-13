import requests
import sys

def test_cors_headers(url):
    """
    Test if a URL returns proper CORS headers in response to OPTIONS and GET requests.
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
        print("Headers:")
        for name, value in options_response.headers.items():
            if name.lower().startswith('access-control'):
                print(f"  {name}: {value}")
        
        # Check if key CORS headers are present
        has_allow_origin = any(h.lower() == 'access-control-allow-origin' for h in options_response.headers)
        has_allow_methods = any(h.lower() == 'access-control-allow-methods' for h in options_response.headers)
        
        if has_allow_origin and has_allow_methods:
            print("✅ OPTIONS request has proper CORS headers")
        else:
            print("❌ OPTIONS request is missing required CORS headers")
    except Exception as e:
        print(f"❌ OPTIONS request failed: {e}")
    
    # Test GET request
    headers = {
        'Origin': 'https://proto-ux.netlify.app',
    }
    
    try:
        get_response = requests.get(url, headers=headers, timeout=10)
        print("\nGET Request:")
        print(f"Status Code: {get_response.status_code}")
        print("Headers:")
        for name, value in get_response.headers.items():
            if name.lower().startswith('access-control'):
                print(f"  {name}: {value}")
        
        # Check if key CORS headers are present
        has_allow_origin = any(h.lower() == 'access-control-allow-origin' for h in get_response.headers)
        
        if has_allow_origin:
            print("✅ GET request has proper CORS headers")
        else:
            print("❌ GET request is missing required CORS headers")
    except Exception as e:
        print(f"❌ GET request failed: {e}")

if __name__ == "__main__":
    # Default URL to test
    test_url = "https://proto-api-kg9r.onrender.com/toolkit/web-metrics/business/?page_id=54"
    
    # Allow command-line override
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    test_cors_headers(test_url)
    print("\nRun this script after deploying the changes to verify if CORS is working correctly.") 