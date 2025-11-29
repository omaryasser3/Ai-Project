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
api_key = "AIzaSyDv_t2MopcX0IqrRIBfFeWjhN6yTKZSfb0"
genai.configure(api_key=api_key)
def call_llm(model_name, prompt, temp=0.2):
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt,generation_config=genai.types.GenerationConfig(temperature=temp))
            return response.text

def translator_agent(code_snippet, src_lang, trg_lang=None, decide=True):
    model_name = config['models']['translator']

    if (decide):
        prompt = f"""
        You are an expert program repair system. 
        You need to analyze the given bug and decide which programming language to translate it to for the next repair iteration. You should make the analysis step by step. 
        Code: {code_snippet}
        Task 1 Description: The task is to translate the bugs that cannot be fixed in one programming language to another programming language. 
            You need to analyze the current bug and decide which programming language to translate it to for the next repair iteration.
            Provide a justification for your decision step by step.
        Task 2 Description: Translate the code from {src_lang} to your chosen programming lanaguge. Do not output any extra description or tokens other than the translated code.
        Output style: Formate the output in a JSON file as such: \{"language":"the language you decided to translate to", "translated_code":"your translation of the code\}
        """
        return call_llm(model_name, prompt)

    else:
        prompt = f"""
        You are an expert code translator.
        Code = {code_snippet}
        Task Description: Here is code in {src_lang} programming lanaguge. Translate the code from {src_lang} to {trg_lang} programming lanaguge. 
            Do not output any extra description or tokens other than the translated code. 
        """

def analyzer_agent(code_snippet, language):
    model_name = config['models']['complex_analyzer']
    
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
    model_name = config['models']['complex_fixer']
    
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
