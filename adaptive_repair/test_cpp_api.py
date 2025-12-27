"""
Test C++ unsupported language handling via the web API
"""
import requests
import json

# Buggy C++ code - off-by-one error in array indexing
BUGGY_CPP_CODE = '''
#include <iostream>
#include <vector>

int findMax(std::vector<int> arr) {
    int max_val = arr[0];
    // BUG: should be i < arr.size(), not i <= arr.size()
    // This will cause array out of bounds access
    for (int i = 1; i <= arr.size(); i++) {
        if (arr[i] > max_val) {
            max_val = arr[i];
        }
    }
    return max_val;
}

int main() {
    std::vector<int> numbers = {3, 7, 2, 9, 1};
    std::cout << "Max: " << findMax(numbers) << std::endl;
    return 0;
}
'''

API_URL = "http://127.0.0.1:5000/api/repair"

def test_cpp_unsupported():
    print("=" * 70)
    print("Testing C++ Unsupported Language Handling")
    print("=" * 70)
    
    payload = {
        "code": BUGGY_CPP_CODE,
        "language": "C++",
        "request_id": "test_cpp_unsupported"
    }
    
    print("\nSending C++ code to repair endpoint...")
    print(f"Code length: {len(BUGGY_CPP_CODE)} characters")
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\nResponse:")
            print("-" * 70)
            print(f"Final Code: {data.get('final_code', 'N/A')[:100]}...")
            
            # Check test validation
            test_validation = data.get('test_validation', {})
            if test_validation:
                print("\nTest Validation:")
                execution = test_validation.get('execution', {})
                print(f"  Execution Success: {execution.get('execution_success', False)}")
                print(f"  Output: {execution.get('output', 'N/A')[:200]}")
                print(f"  Summary: {execution.get('summary', {})}")
                
                # Check if it contains unsupported language message
                output = execution.get('output', '')
                if 'Unsupported language' in output:
                    print("\n✓ Unsupported language error message displayed correctly!")
                    print(f"✓ Error mentions Python and Java: {'Python and Java' in output}")
                else:
                    print("\n✗ Expected unsupported language error not found")
            else:
                print("\nNo test validation in response (expected for unsupported languages)")
            
        else:
            print(f"\nError: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server. Is it running on port 5000?")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    test_cpp_unsupported()
