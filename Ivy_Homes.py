import requests
import json
from datetime import datetime
import time
from collections import deque

# List of API endpoints
API_ENDPOINTS = [
    "http://35.200.185.69:8000/v1/autocomplete",
    "http://35.200.185.69:8000/v2/autocomplete",
    "http://35.200.185.69:8000/v3/autocomplete",
]

TOTAL_REQUESTS = 0
REQUEST_TIMEOUT = 10  # Seconds to wait before timeout
CUSTOM_HEADERS = {"User-Agent": "Mozilla/5.0"}

# Track usage and errors per endpoint
ENDPOINT_USAGE = {url: 0 for url in API_ENDPOINTS}
ENDPOINT_ERRORS = {url: 0 for url in API_ENDPOINTS}

# Queue for cycling through endpoints
ENDPOINT_CYCLE = deque(API_ENDPOINTS)

def fetch_next_endpoint():
    """Cycle through endpoints for balanced load distribution."""
    ENDPOINT_CYCLE.rotate(-1)
    return ENDPOINT_CYCLE[0]

def send_api_request(search_term: str):
    """Distribute requests across endpoints with failover support."""
    global TOTAL_REQUESTS
    TOTAL_REQUESTS += 1
    
    # Attempt each endpoint until success
    for _ in range(len(API_ENDPOINTS)):
        selected_endpoint = fetch_next_endpoint()
        ENDPOINT_USAGE[selected_endpoint] += 1
        
        try:
            request_start = time.time()
            api_response = requests.get(
                selected_endpoint, 
                params={"query": search_term}, 
                headers=CUSTOM_HEADERS, 
                timeout=REQUEST_TIMEOUT
            )
            duration = time.time() - request_start
            
            if api_response.status_code == 429:
                ENDPOINT_ERRORS[selected_endpoint] += 1
                print(f"Hit rate limit on {selected_endpoint.split('/')[-2]}. Switching endpoints...")
                continue
                
            print(f"\nSearch: '{search_term}' | Endpoint: {selected_endpoint.split('/')[-2]} | "
                  f"Code: {api_response.status_code} | Duration: {duration:.3f}s")
            print(f"Data: {api_response.text[:100]}..." if len(api_response.text) > 100 else f"Data: {api_response.text}")
            
            if api_response.status_code == 200:
                return api_response.json()
            else:
                ENDPOINT_ERRORS[selected_endpoint] += 1
                print(f"Failed on {selected_endpoint.split('/')[-2]}, moving to next...")
                
        except requests.exceptions.RequestException as err:
            ENDPOINT_ERRORS[selected_endpoint] += 1
            print(f"API call failed for '{search_term}' on {selected_endpoint.split('/')[-2]}: {err}")
    
    print(f"All endpoints exhausted for search: '{search_term}'")
    return None

def gather_all_names():
    """Recursively collect all names from the API starting with alphabet letters."""
    pending_searches = set()
    collected_names = []
    initial_chars = {chr(i) for i in range(ord('a'), ord('z') + 1)}
    pending_searches.update(initial_chars)

    print("\nInitiating name collection from API...")
    begin_time = datetime.now()

    while pending_searches:
        current_term = pending_searches.pop()
        collected_names.append(current_term)

        api_data = send_api_Request(current_term)
        if api_data and isinstance(api_data, dict) and "results" in api_data:
            found_names = set(api_data["results"])
            fresh_names = found_names - set(collected_names)

            if fresh_names:
                pending_searches.update(fresh_names)
                print(f"Term '{current_term}': Discovered {len(found_names)} names, {len(fresh_names)} unique")
            else:
                print(f"Term '{current_term}': No unique names")
        else:
            print(f"Term '{current_term}': No data retrieved")

    finish_time = datetime.now()
    total_duration = (finish_time - begin_time).total_seconds()
    
    print(f"\nCollection finished!")
    print(f"Unique names collected: {len(collected_names)}")
    print(f"API calls made: {TOTAL_REQUESTS}")
    print(f"Duration: {total_duration:.2f} seconds")
    
    print("\nEndpoint Metrics:")
    for endpoint in API_ENDPOINTS:
        endpoint_id = endpoint.split('/')[-2]
        success_pct = ((ENDPOINT_USAGE[endpoint] - ENDPOINT_ERRORS[endpoint]) / ENDPOINT_USAGE[endpoint] * 100) if ENDPOINT_USAGE[endpoint] > 0 else 0
        print(f"  {endpoint_id}: {ENDPOINT_USAGE[endpoint]} calls, {ENDPOINT_ERRORS[endpoint]} errors, {success_pct:.1f}% success")

    return {
        "names": sorted(collected_names),
        "duration": total_duration,
        "call_count": TOTAL_REQUESTS,
        "endpoint_metrics": {url.split('/')[-2]: {"calls": ENDPOINT_USAGE[url], "errors": ENDPOINT_ERRORS[url]} for url in API_ENDPOINTS}
    }

if __name__ == "__main__":
    print("Checking endpoint availability with a test query...")
    for endpoint in API_ENDPOINTS:
        endpoint_id = endpoint.split('/')[-2]
        try:
            test_response = requests.get(endpoint, params={"query": "a"}, headers=CUSTOM_HEADERS, timeout=REQUEST_TIMEOUT)
            print(f"Endpoint {endpoint_id}: Code {test_response.status_code}")
        except requests.exceptions.RequestException as err:
            print(f"Endpoint {endpoint_id}: Failed - {err}")
    
    results = gather_all_names()

    print("\nResults Overview:")
    print(f"Unique names: {len(results['names'])}")
    print(f"Total API calls: {results['call_count']}")
    print(f"Time taken: {results['duration']:.2f}s")
    
    output_filename = f"names_collected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, "w") as outfile:
        json.dump(results, outfile, indent=2)
    print(f"Data exported to {output_filename}")