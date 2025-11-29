import os
import yaml
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

api_key = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=api_key)


def call_llm(model_name, prompt, temp=0.2):
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt,generation_config=genai.types.GenerationConfig(temperature=temp))
            return response.text

def analyzer_agent(code_snippet, language):
    model_name = config['models'].get('complex_fixer', 'gemini-2.5-flash-preview-09-2025')
    
    prompt = f"""
    You are an expert code analyzer.
    Your task is to analyze the following {language} code to identify the bug.
    
    1. Explain what the code is trying to do.
    2. Identify the specific line(s) where the bug is.
    3. Explain WHY it is a bug.
    
    Return your analysis in clear text.
    
    Code:
    {code_snippet}
    """
    return call_llm(model_name, prompt)

def fixer_agent(code_snippet, language, analysis):
    # Use the 'simple_fixer' or 'complex_fixer' model from config, or default to a standard one
    model_name = config['models'].get('complex_fixer', 'gemini-2.5-flash-preview-09-2025')
    
    prompt = f"""
    You are an expert software engineer.
    Your task is to fix the bug in the following {language} code.
    
    Use the provided analysis to guide your fix.
    
    Analysis:
    {analysis}
    
    Code:
    {code_snippet}
    
    Return ONLY the corrected code. Do not include markdown formatting like ```python or ```.
    """
    
    response = call_llm(model_name, prompt)
    return response.replace("```", "").strip()
