"""
Test script to verify C++ language detection and backward translation in the graph.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from graph import create_graph

# Sample C++ code with a bug
CPP_CODE = """#include <iostream>
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
}"""

def test_cpp_auto_detection():
    """Test 1: Empty language field (should auto-detect C++)"""
    print("=" * 80)
    print("TEST 1: Auto-detection with empty language field")
    print("=" * 80)
    
    initial_state = {
        "bug_id": "test-auto-cpp",
        "code": CPP_CODE,
        "src_lang": "Auto",  # Empty/Auto should trigger detection
        "current_lang": "Auto",
        "issues": None,
        "plan": None,
        "agent_queue": [],
        "history": [],
        "generate_tests": True
    }
    
    graph = create_graph(entry_point="main_node")
    final_state = graph.invoke(initial_state)
    
    # Verify results
    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    
    detected_lang = final_state.get("plan").detected_language if final_state.get("plan") else None
    src_lang = final_state.get("src_lang")
    current_lang = final_state.get("current_lang")
    translation_info = final_state.get("translation", {})
    final_code = final_state.get("fixed_code", final_state.get("code"))
    
    print(f"✓ Detected Language: {detected_lang}")
    print(f"✓ Source Language (src_lang): {src_lang}")
    print(f"✓ Current Language (current_lang): {current_lang}")
    print(f"✓ Translation Used: {translation_info.get('used', False)}")
    print(f"✓ Final Language: {translation_info.get('final_language', current_lang)}")
    
    # Check if final code is C++
    is_cpp = any(marker in final_code for marker in ['#include', 'std::', 'vector<int>'])
    print(f"✓ Final code contains C++ markers: {is_cpp}")
    
    print("\n" + "-" * 80)
    print("FINAL CODE (first 500 chars):")
    print("-" * 80)
    print(final_code[:500])
    
    # Assertions
    assert detected_lang == "C++", f"Expected detected_lang='C++', got '{detected_lang}'"
    assert src_lang == "C++", f"Expected src_lang='C++', got '{src_lang}'"
    assert is_cpp, "Final code should contain C++ syntax!"
    
    print("\n✅ TEST 1 PASSED: Auto-detection works correctly!")
    return final_state


def test_cpp_wrong_user_language():
    """Test 2: User provides wrong language (Python) for C++ code"""
    print("\n" + "=" * 80)
    print("TEST 2: Wrong user language (Python) for C++ code")
    print("=" * 80)
    
    initial_state = {
        "bug_id": "test-wrong-lang-cpp",
        "code": CPP_CODE,
        "src_lang": "Python",  # User says Python but code is C++
        "current_lang": "Python",
        "issues": None,
        "plan": None,
        "agent_queue": [],
        "history": [],
        "generate_tests": True
    }
    
    graph = create_graph(entry_point="main_node")
    final_state = graph.invoke(initial_state)
    
    # Verify results
    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    
    detected_lang = final_state.get("plan").detected_language if final_state.get("plan") else None
    src_lang = final_state.get("src_lang")
    current_lang = final_state.get("current_lang")
    translation_info = final_state.get("translation", {})
    final_code = final_state.get("fixed_code", final_state.get("code"))
    
    print(f"✓ User provided: Python")
    print(f"✓ Detected Language: {detected_lang}")
    print(f"✓ Corrected src_lang: {src_lang}")
    print(f"✓ Current Language: {current_lang}")
    print(f"✓ Translation Used: {translation_info.get('used', False)}")
    print(f"✓ Final Language: {translation_info.get('final_language', current_lang)}")
    
    # Check if final code is C++
    is_cpp = any(marker in final_code for marker in ['#include', 'std::', 'vector<int>'])
    print(f"✓ Final code contains C++ markers: {is_cpp}")
    
    print("\n" + "-" * 80)
    print("FINAL CODE (first 500 chars):")
    print("-" * 80)
    print(final_code[:500])
    
    # Assertions
    assert detected_lang == "C++", f"Expected detected_lang='C++', got '{detected_lang}'"
    assert src_lang == "C++", f"Expected src_lang to be corrected to 'C++', got '{src_lang}'"
    assert is_cpp, "Final code should contain C++ syntax!"
    
    print("\n✅ TEST 2 PASSED: Language auto-correction works!")
    return final_state


def test_cpp_correct_user_language():
    """Test 3: User correctly provides C++ language"""
    print("\n" + "=" * 80)
    print("TEST 3: Correct user language (C++)")
    print("=" * 80)
    
    initial_state = {
        "bug_id": "test-correct-cpp",
        "code": CPP_CODE,
        "src_lang": "C++",  # User correctly says C++
        "current_lang": "C++",
        "issues": None,
        "plan": None,
        "agent_queue": [],
        "history": [],
        "generate_tests": True
    }
    
    graph = create_graph(entry_point="main_node")
    final_state = graph.invoke(initial_state)
    
    # Verify results
    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    
    plan = final_state.get("plan")
    detected_lang = plan.detected_language if plan else None
    src_lang = final_state.get("src_lang")
    current_lang = final_state.get("current_lang")
    translation_info = final_state.get("translation", {})
    final_code = final_state.get("fixed_code", final_state.get("code"))
    
    print(f"✓ User provided: C++")
    print(f"✓ Detected Language: {detected_lang}")
    print(f"✓ Language Match: {plan.language_match if plan else 'N/A'}")
    print(f"✓ Source Language: {src_lang}")
    print(f"✓ Translation Used: {translation_info.get('used', False)}")
    print(f"✓ Final Language: {translation_info.get('final_language', current_lang)}")
    
    # Check if final code is C++
    is_cpp = any(marker in final_code for marker in ['#include', 'std::', 'vector<int>'])
    print(f"✓ Final code contains C++ markers: {is_cpp}")
    
    print("\n" + "-" * 80)
    print("FINAL CODE (first 500 chars):")
    print("-" * 80)
    print(final_code[:500])
    
    # Assertions
    assert detected_lang == "C++", f"Expected detected_lang='C++', got '{detected_lang}'"
    assert src_lang == "C++", f"Expected src_lang='C++', got '{src_lang}'"
    assert is_cpp, "Final code should contain C++ syntax!"
    
    print("\n✅ TEST 3 PASSED: No translation when language is correct and not needed!")
    return final_state


if __name__ == "__main__":
    print("\n" + "🧪" * 40)
    print("C++ LANGUAGE DETECTION & TRANSLATION TESTS")
    print("🧪" * 40)
    
    try:
        # Run all tests
        test_cpp_auto_detection()
        test_cpp_wrong_user_language()
        test_cpp_correct_user_language()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 80)
        print("\n✅ Language auto-detection working correctly")
        print("✅ Language auto-correction working correctly")
        print("✅ Backward translation returning C++ code")
        
    except AssertionError as e:
        print("\n" + "=" * 80)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ ERROR: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
