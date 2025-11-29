import google.generativeai as genai
import os

# Use the key provided by the user in the previous step (hardcoded for this check)
# In a real scenario, we should be careful, but the user explicitly put it in the code.
api_key = "AIzaSyDv_t2MopcX0IqrRIBfFeWjhN6yTKZSfb0"
genai.configure(api_key=api_key)

print("Listing available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
