import os
import json
import logging
import re
from dataclasses import dataclass
from typing import List, Literal, Optional

import yaml
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time

try:
    from dotenv import load_dotenv
    # Load from current directory or parents
    load_dotenv()
    # Also try explicit path if running from src
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass



# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------

def strip_markdown_code_block(code: str) -> str:
    """Robustly strips markdown code fences from the code string."""
    if not code:
        return code
    
    # Remove empty lines from start/end
    lines = code.strip().splitlines()
    if not lines:
        return code
        
    # Check first line for fence
    if lines[0].strip().startswith("```"):
        lines = lines[1:]
        
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
        
    return "\n".join(lines).strip()

def get_java_helper_code():
    """Reads Node.java to provide context for Java repairs."""
    try:
        # data/java_programs/Node.java relative to src/agents.py
        node_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "java_programs", "Node.java")
        if os.path.exists(node_path):
            with open(node_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.warning(f"Failed to read Node.java: {e}")
    return ""

# ---------------------------------------------------------------------------
# Configuration & Logging
# ---------------------------------------------------------------------------

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


import google.api_core.exceptions

# ---------------------------------------------------------------------------
# Global Key Management
# ---------------------------------------------------------------------------

_API_KEYS: List[str] = []
_CURRENT_KEY_INDEX: int = 0

def _load_api_keys() -> None:
    """Load all available API keys from environment variables."""
    global _API_KEYS
    _API_KEYS = []

    # 1. Try comma-separated list
    keys_str = os.getenv("GEMINI_API_KEYS")
    if keys_str:
        _API_KEYS.extend([k.strip() for k in keys_str.split(",") if k.strip()])

    # 2. Try indexed keys (GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.)
    i = 1
    while True:
        k = os.getenv(f"GEMINI_API_KEY_{i}")
        if not k:
            break
        _API_KEYS.append(k.strip())
        i += 1

    # 3. Fallback to single key (or comma-separated string)
    if not _API_KEYS:
        single_key = os.getenv("GEMINI_API_KEY")
        if single_key:
            if "," in single_key:
                _API_KEYS.extend([k.strip() for k in single_key.split(",") if k.strip()])
            else:
                _API_KEYS.append(single_key.strip())
            
    if not _API_KEYS:
        raise RuntimeError(
            "No Gemini API keys found. Please set GEMINI_API_KEYS, "
            "GEMINI_API_KEY_n, or GEMINI_API_KEY."
        )

def _configure_genai() -> None:
    """Configure Gemini using the current API key."""
    global _API_KEYS, _CURRENT_KEY_INDEX
    
    if not _API_KEYS:
        _load_api_keys()
        
    current_key = _API_KEYS[_CURRENT_KEY_INDEX]
    genai.configure(api_key=current_key)
    # logger.info(f"Configured GenAI with key index {_CURRENT_KEY_INDEX} (ending in ...{current_key[-4:]})")

def _rotate_key() -> bool:
    """Switch to the next available API key. Returns True if successful, False if all exhausted."""
    global _CURRENT_KEY_INDEX, _API_KEYS
    
    _CURRENT_KEY_INDEX += 1
    if _CURRENT_KEY_INDEX >= len(_API_KEYS):
        # We've run out of keys
        return False
    
    # Re-configure with the new key
    _configure_genai()
    logger.warning(f"Key exhausted! Rotated to key index {_CURRENT_KEY_INDEX}.")
    return True

def call_llm(model_name: str, prompt: str, temp: float = 0.2) -> str:
    """Wrapper around Gemini API with automatic key rotation on quota failure."""
    
    # Ensure initialized
    if not _API_KEYS:
        _configure_genai()

    while True:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=temp),
            )
            text = getattr(response, "text", "") or ""
            return text
            
        except google.api_core.exceptions.ResourceExhausted:
            logger.warning(f"Quota exceeded for key index {_CURRENT_KEY_INDEX}.")
            if not _rotate_key():
                logger.critical("All API keys exhausted during call_llm.")
                raise Exception("All API keys exhausted")
            # Loop continues with new key
            
        except Exception as e:
            # Check for invalid API key error (400)
            if "400" in str(e) and ("API_KEY_INVALID" in str(e) or "not valid" in str(e).lower()):
                logger.warning(f"API key is invalid. Rotating to next key...")
                if not _rotate_key():
                    logger.critical("All API keys exhausted during call_llm.")
                    raise Exception("All API keys exhausted")
                # Loop continues with new key
            # Check for leaked API key error (403)
            elif "403" in str(e) and "leaked" in str(e).lower():
                logger.warning(f"API key reported as leaked. Rotating to next key...")
                if not _rotate_key():
                    logger.critical("All API keys exhausted during call_llm.")
                    raise Exception("All API keys exhausted")
                # Loop continues with new key
            # Check for "429" in string representation if exception type isn't caught
            elif "429" in str(e) or "Resource has been exhausted" in str(e):
                logger.warning(f"Quota error detected: {e}")
                if not _rotate_key():
                    logger.critical("All API keys exhausted during call_llm.")
                    raise Exception("All API keys exhausted")
                # Loop continues
            else:
                logger.error(f"Error calling LLM model '{model_name}': {e}")
                raise

def translator_agent(code_snippet, src_lang, trg_lang=None, decide=True, bug_id=None):
    model_name = config['models']['translator']

    if (decide):
        prompt = f"""
        You are an expert program repair system. 
        You need to analyze the given bug and decide which programming language to translate it to for the next repair iteration. You should make the analysis step by step. 
        Code: {code_snippet}
        Task 1 Description: The task is to translate the bugs that cannot be fixed in one programming language to another programming language. 
            You need to analyze the current bug and decide which programming language to translate it to for the next repair iteration.
            Provide a justification for your decision step by step.
        Task 2 Description: Translate the code from {src_lang} to your chosen programming language. Do not output any extra description or tokens other than the translated code.
        Output style: Format the output in a JSON file as such: {{"language":"the language you decided to translate to", "translated_code":"your translation of the code"}}
        Return ONLY the JSON object. Do not include markdown formatting like ```json or ```.
        """
        response = call_llm(model_name, prompt)
        return response.replace("```json", "").replace("```", "").strip()


    else:
        prompt = f"""
        You are an expert code translator.
        Code = {code_snippet}
        Task Description: Here is code in {src_lang} programming language. Translate the code from {src_lang} to {trg_lang} programming language. 
            Do not output any extra description or tokens other than the translated code. 
            Do NOT wrap the code in markdown blocks (e.g. ```{trg_lang}).{f'''
            CRITICAL: The code MUST use the public class name `{bug_id}`. The file name is `{bug_id}.java`. The package should be `java_programs`.''' if bug_id and trg_lang.lower() == 'java' else ''}
        """
        raw = call_llm(model_name, prompt)
        return strip_markdown_code_block(raw)

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
    return strip_markdown_code_block(response)


# ---------------------------------------------------------------------------
# New Agent System for Automatic Program Repair (Python-only entry point)
# ---------------------------------------------------------------------------

IssueType = Literal["syntax_error", "logic_bug", "performance_issue", "style_issue"]


@dataclass
class Issue:
    """Represents a single problem found in the code."""

    id: int
    type: IssueType
    description: str
    location_hint: Optional[str] = None  # e.g., "line 10", "function foo"


@dataclass
class RepairResult:
    """Result produced by a specialized agent when attempting a repair."""

    fixed_code: str
    explanation: str


@dataclass
class RepairPlan:
    """High-level plan decided by the MainAgent for how to repair the code.

    - translate: whether to translate to another language before repairing
    - target_language: language to translate to (e.g., "Java"), if translate is True
    - detected_language: language inferred from the actual code snippet
    - language_match: whether detected_language matches the declared src_language
    """

    translate: bool
    target_language: Optional[str] = None
    detected_language: Optional[str] = None
    language_match: Optional[bool] = None


class BaseAgent:
    """Base class for all repair agents."""

    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.2):
        self.model_name = model_name or config["models"].get("worker", "gemini-2.5-flash")
        self.temperature = temperature

    def repair(self, code: str, issue: Issue, language: str, bug_id: str = None) -> RepairResult:
        """Subclasses must implement this to perform the actual repair."""
        raise NotImplementedError

    def _extract_json(self, text: str) -> dict:
        """Robustly valid JSON object from a string that might contain other text."""
        # First try direct parsing
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to clean markdown code blocks
        clean_text = text.replace("```json", "").replace("```", "")
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass
            
        # Try to find the first { and last }
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = text[start : end + 1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback: If JSON parsing fails, try to extract code block directly
        # This handles cases where the model outputs invalid JSON (e.g. multiline strings)
        # but does provide a code block.
        # We look for ```language ... ```
        # We can't know the language easily here without passing it, so we accept generic ```
        
        code_block_pattern = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)
        match = code_block_pattern.search(text)
        if match:
            # Construct a fake JSON object
            return {
                "fixed_code": match.group(1),
                "explanation": "Extracted directly from code block after JSON parse failure."
            }
        
        raise ValueError("Could not extract valid JSON from response")

    def _strip_markdown(self, code: str) -> str:
        """Robustly strips markdown code fences from the code string."""
        return strip_markdown_code_block(code)


class SyntaxAgent(BaseAgent):
    """Agent focused on resolving syntax and parsing errors."""

    def repair(self, code: str, issue: Issue, language: str, bug_id: str = None) -> RepairResult:
        helper_context = ""
        if language.lower() == "java":
            node_code = get_java_helper_code()
            if node_code:
                helper_context = f"\n\nReference Helper Class (Node.java):\n```java\n{node_code}\n```\n"

        prompt = f"""
        You are an expert {language} compiler and code fixer.

        Your task is to fix ONLY the syntax or parsing issues in the following {language} code.

        Issue description:
        {issue.description}
        {helper_context}

        Current code:
        ```{language}
        {code}
        ```

        Requirements:
        - Return valid, executable {language} code that is syntactically correct.
        - Do NOT change the overall logic beyond what is required to fix syntax.
        - After the code, provide a short explanation (2–4 sentences) of what you changed and why.{f'''
        - CRITICAL: PRESERVE EXACT METHOD NAMES - Do NOT rename methods (e.g., do NOT change snake_case to camelCase, do NOT change `get_factors` to `getFactors`).
        - CRITICAL: PRESERVE EXACT RETURN TYPES - Do NOT change return types (e.g., do NOT change `ArrayList` to `List`, do NOT change concrete types to interfaces).
        - CRITICAL: PRESERVE EXACT PARAMETER TYPES - Do NOT change parameter types (e.g., do NOT change `ArrayList` to `int[]`, keep exact types from original code).
        - CRITICAL: PRESERVE ACCESS MODIFIERS - Do NOT change `public` to package-private, keep `public class`, `public method` exactly as in original.
        - CRITICAL: The code MUST use the public class name `{bug_id}`. The file name is `{bug_id}.java`. The package should be `java_programs`. Do not use `Solution` or generic names.''' if bug_id and language.lower() == 'java' else ''}
        - Do NOT wrap the code in markdown blocks (e.g. ```{language}) INSIDE the JSON string.
        - Use \\n for newlines inside the JSON string value.

        Output format (JSON):
        {{
          "fixed_code": "<fixed {language} code>",
          "explanation": "<short explanation of the changes>"
        }}

        Return ONLY the JSON object, without any markdown fences.
        """
        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        
        try:
            data = self._extract_json(raw)
        except ValueError:
            logger.warning(f"SyntaxAgent: failed to parse JSON response. Raw: {raw[:100]}...")
            return RepairResult(
                fixed_code=code,
                explanation=f"Failed to parse model response as JSON. Raw response: {raw}",
            )

        fixed_code = data.get("fixed_code", code)
        fixed_code = self._strip_markdown(fixed_code)
            
        return RepairResult(
            fixed_code=fixed_code,
            explanation=data.get("explanation", "No explanation provided by the model."),
        )


class LogicAgent(BaseAgent):
    """Agent focused on fixing logical/semantic bugs."""

    def repair(self, code: str, issue: Issue, language: str, bug_id: str = None, user_feedback: str = None) -> RepairResult:
        helper_context = ""
        if language.lower() == "java":
            node_code = get_java_helper_code()
            if node_code:
                helper_context = f"\n\nReference Helper Class (Node.java):\n```java\n{node_code}\n```\n"

        prompt = f"""
        You are an expert {language} software engineer.

        The following {language} code has a LOGICAL or SEMANTIC bug, not just syntax.

        Issue description:
        {issue.description}
        {helper_context}

        Buggy code:
        ```{language}
        {code}
        ```
        {f'''
        USER FEEDBACK:
        The user has provided specific feedback for this repair. You MUST follow these instructions:
        "{user_feedback}"
        ''' if user_feedback else ''}

        Tasks:
        1. Correct the logic so the code behaves as intended.
        2. Preserve the overall structure and style as much as possible.{f'''
        3. CRITICAL: PRESERVE EXACT METHOD NAMES - Do NOT rename methods (e.g., keep snake_case as snake_case, do NOT change to camelCase).
        4. CRITICAL: PRESERVE EXACT RETURN TYPES - Do NOT change return types (e.g., keep `ArrayList` as `ArrayList`, do NOT change to `List`).
        5. CRITICAL: PRESERVE EXACT PARAMETER TYPES - Do NOT modify parameter types or signatures.
        6. CRITICAL: PRESERVE ACCESS MODIFIERS - Do NOT change `public` classes or methods to package-private.
        7. CRITICAL: The code MUST use the public class name `{bug_id}`. The file name is `{bug_id}.java`. The package should be `java_programs`. ''' if bug_id and language.lower() == 'java' else ''}
        
        Output format (JSON):
        {{
          "fixed_code": "<corrected {language} code>",
          "explanation": "<short explanation of what was wrong and how you fixed it>"
        }}

        Return ONLY the JSON object, without any markdown. Use \\n for newlines in code strings.
        """
        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        
        try:
            data = self._extract_json(raw)
        except ValueError:
            logger.warning(f"LogicAgent: failed to parse JSON response. Raw: {raw[:100]}...")
            return RepairResult(
                fixed_code=code,
                explanation=f"Failed to parse model response as JSON. Raw response: {raw}",
            )

        fixed_code = data.get("fixed_code", code)
        fixed_code = self._strip_markdown(fixed_code)

        return RepairResult(
            fixed_code=fixed_code,
            explanation=data.get("explanation", "No explanation provided by the model."),
        )


class OptimizationAgent(BaseAgent):
    """Agent focused on performance and efficiency improvements."""

    def repair(self, code: str, issue: Issue, language: str, bug_id: str = None) -> RepairResult:
        helper_context = ""
        if language.lower() == "java":
            node_code = get_java_helper_code()
            if node_code:
                helper_context = f"\n\nReference Helper Class (Node.java):\n```java\n{node_code}\n```\n"

        prompt = f"""
        You are an expert {language} performance engineer.

        Optimize the following {language} code for better performance and/or memory efficiency,
        while preserving its external behavior.

        Performance issue description:
        {issue.description}
        {helper_context}

        Original code:
        ```{language}
        {code}
        ```

        Tasks:
        1. Improve the performance/efficiency of the code where possible.
        2. Preserve correctness and overall behavior.
        3. Keep the structure as clean and readable as you can.{f'''
        4. CRITICAL: PRESERVE EXACT METHOD NAMES - Do NOT rename methods.
        5. CRITICAL: PRESERVE EXACT RETURN TYPES - Do NOT change return types.
        6. CRITICAL: PRESERVE EXACT PARAMETER TYPES - Do NOT modify method signatures.
        7. CRITICAL: PRESERVE ACCESS MODIFIERS - Do NOT remove `public` from classes or methods.
        8. CRITICAL: The code MUST use the public class name `{bug_id}`. The file name is `{bug_id}.java`. The package should be `java_programs`. Do not use `Solution` or generic names.''' if bug_id and language.lower() == 'java' else ''}

        Output format (JSON):
        {{
          "fixed_code": "<optimized {language} code>",
          "explanation": "<short explanation of the optimizations>"
        }}

        Return ONLY the JSON object, without any markdown. Use \\n for newlines in code strings.
        """
        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        
        try:
            data = self._extract_json(raw)
        except ValueError:
            logger.warning(f"OptimizationAgent: failed to parse JSON response. Raw: {raw[:100]}...")
            return RepairResult(
                fixed_code=code,
                explanation=f"Failed to parse model response as JSON. Raw response: {raw}",
            )

        fixed_code = data.get("fixed_code", code)
        fixed_code = self._strip_markdown(fixed_code)

        return RepairResult(
            fixed_code=fixed_code,
            explanation=data.get("explanation", "No explanation provided by the model."),
        )


class ExplanationAgent(BaseAgent):
    """Agent focused on generating comprehensive, human-readable explanations of repairs.
    
    This agent enhances transparency and explainability by providing:
    - Overall summary of all changes made
    - Detailed explanations of each repair
    - Risk assessment and confidence scoring
    """

    def generate_explanation(self, original_code: str, fixed_code: str, repairs: List[dict], language: str) -> dict:
        """Generate a comprehensive explanation of all repairs made.
        
        Args:
            original_code: The original buggy code
            fixed_code: The repaired code
            repairs: List of repair records from the history
            language: Programming language
            
        Returns:
            dict with 'summary', 'detailed_explanations', and 'confidence_score'
        """
        # Build context from repairs
        repairs_context = ""
        for idx, repair in enumerate(repairs, 1):
            step = repair.get("step", "Unknown")
            issue = repair.get("issue", {})
            explanation = repair.get("explanation", "No explanation")
            
            repairs_context += f"""
Repair #{idx} ({step}):
- Issue Type: {issue.get('type', 'unknown')}
- Issue Description: {issue.get('description', 'N/A')}
- Location: {issue.get('location_hint', 'N/A')}
- What was done: {explanation}
"""

        prompt = f"""
You are an expert code explainer and technical writer.

Your task is to generate a comprehensive, human-readable explanation of the code repairs that were performed.

**Original Code:**
```{language}
{original_code}
```

**Fixed Code:**
```{language}
{fixed_code}
```

**Repairs Applied:**
{repairs_context}

**Your Task:**
1. Provide an **overall summary** (2-3 sentences) explaining what was wrong and what was fixed.
2. For each repair, provide a **detailed explanation** in simple terms that a developer can understand:
   - What was the specific problem?
   - Why did it occur?
   - How was it fixed?
   - What is the impact of this fix?
3. Assign a **confidence score** (0-100) indicating how confident you are that the repairs are correct and complete.
4. List any **potential risks** or **remaining concerns** (if any).

**Output Format (JSON):**
{{
  "summary": "Brief overall summary of all changes",
  "detailed_explanations": [
    {{
      "repair_number": 1,
      "title": "Short descriptive title",
      "problem": "What was wrong",
      "cause": "Why it occurred",
      "solution": "How it was fixed",
      "impact": "Effect of the fix"
    }}
  ],
  "confidence_score": 85,
  "risks": ["Any potential issues or concerns"],
  "transparency_notes": "Any additional notes about the repair process"
}}

Return ONLY the JSON object, without markdown fences.
"""
        
        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        
        try:
            data = self._extract_json(raw)
        except ValueError:
            logger.warning(f"ExplanationAgent: failed to parse JSON response. Raw: {raw[:100]}...")
            return {
                "summary": "Failed to generate comprehensive explanation.",
                "detailed_explanations": [],
                "confidence_score": 0,
                "risks": ["Explanation generation failed"],
                "transparency_notes": "The system was unable to generate a detailed explanation."
            }
        
        return data


class MainAgent(BaseAgent):
    """Main AI agent that analyzes buggy Python code and spawns specialized sub-agents."""

    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.2):
        super().__init__(model_name or config["models"].get("router", "gemini-2.5-flash"), temperature)

    def _parse_issues(self, data: dict) -> List[Issue]:
        issues_data = data.get("issues", []) or []
        issues: List[Issue] = []
        for idx, item in enumerate(issues_data, start=1):
            try:
                issue_type = item.get("type", "style_issue")
                # Basic guard to keep it within our IssueType set
                if issue_type not in ("syntax_error", "logic_bug", "performance_issue", "style_issue"):
                    issue_type = "style_issue"
                issues.append(
                    Issue(
                        id=item.get("id", idx),
                        type=issue_type,  # type: ignore[arg-type]
                        description=item.get("description", "").strip() or "No description provided.",
                        location_hint=item.get("location_hint"),
                    )
                )
            except Exception as e:
                # logger.warning(f"MainAgent: skipping malformed issue entry {item}: {e}")
                pass
        return issues

    def analyze_and_plan(self, code: str, src_language: str = "Python", user_feedback: Optional[str] = None) -> tuple[List[Issue], RepairPlan]:
        """Analyze buggy code and decide whether to translate before repairing.

        Returns a tuple of (issues, plan).
        The plan indicates if translation should be used and to which language.
        """
        system_instructions = """
        You are a senior multi-language code reviewer and bug triage expert.

        Your job is to:
        1) Inspect the code and determine which programming language it is ACTUALLY written in.
           Compare this with the declared source language and note whether they match.
        2) Analyze the code (respecting its true language) to identify issues.
        3) Decide whether temporarily translating the code to another language
           would make the bug easier to analyze and repair with AI tools.

        Possible issue categories (types):
        - "syntax_error"       : invalid syntax, parsing errors, indentation problems
        - "logic_bug"          : wrong conditions, incorrect algorithms, off-by-one errors, etc.
        - "performance_issue"  : unnecessarily slow, non-optimal complexity, duplicated heavy work
        - "style_issue"        : bad naming, formatting, readability (use sparingly)

        IMPORTANT:
        - Do NOT propose or apply fixes.
        - ONLY describe and categorize the issues and produce a high-level repair plan.

        The repair plan MUST:
        - Indicate whether to translate the code before repairing.
        - If translation is recommended, specify a single target language
          (e.g., "Python", "Java") where AI-based program repair is likely to be most effective.

        Output format (JSON):
        {
          "plan": {
            "detected_language": "Java",
            "language_match": false,
            "translate": true,
            "target_language": "Python"
          },
          "issues": [
            {
              "id": 1,
              "type": "syntax_error",
              "description": "Detailed description of the problem",
              "location_hint": "line 12, in function foo"
            }
          ]
        }

        If no issues are found, return:
        {
          "plan": {
            "detected_language": "Python",
            "language_match": true,
            "translate": false,
            "target_language": null
          },
          "issues": []
        }

        Return ONLY the JSON object, without markdown fences.
        """
        
        feedback_context = ""
        if user_feedback:
            feedback_context = f"\nIMPORTANT USER FEEDBACK (The user rejected the previous repair attempt):\n'{user_feedback}'\nPlease address this feedback specifically in your new analysis and plan."

        prompt = f"""
        {system_instructions}

        Original language of the code: {src_language}
        {feedback_context}

        Here is the code to analyze:
        ```
        {code}
        ```
        """

        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        
        try:
            data = self._extract_json(raw)
        except ValueError:
            logger.error("MainAgent: failed to parse JSON from analysis+plan response.")
            # logger.debug(f"Raw response: {raw}")
            # Fallback: no translation, pseudo-issue to surface the problem
            fallback_plan = RepairPlan(translate=False, target_language=None)
            fallback_issue = Issue(
                id=1,
                type="style_issue",
                description="Failed to parse analysis+plan response as JSON. Raw response stored here.",
                location_hint=None,
            )
            return [fallback_issue], fallback_plan

        issues = self._parse_issues(data)

        plan_data = data.get("plan") or {}
        translate_flag = bool(plan_data.get("translate", False))
        target_language = plan_data.get("target_language")
        detected_language = plan_data.get("detected_language")
        language_match = plan_data.get("language_match")

        # Normalize string fields
        if isinstance(target_language, str):
            target_language = target_language.strip() or None
        if isinstance(detected_language, str):
            detected_language = detected_language.strip() or None

        # Normalize language_match to bool or None
        if isinstance(language_match, str):
            lowered = language_match.strip().lower()
            if lowered in ("true", "yes"):
                language_match = True
            elif lowered in ("false", "no"):
                language_match = False
            else:
                language_match = None
        elif not isinstance(language_match, bool):
            language_match = None

        plan = RepairPlan(
            translate=translate_flag,
            target_language=target_language,
            detected_language=detected_language,
            language_match=language_match,
        )
        return issues, plan

    def analyze_code(self, code: str, src_language: str = "Python") -> List[Issue]:
        """Backward-compatible helper: analyze code and return only issues.

        This wraps analyze_and_plan but discards the plan.
        """
        issues, _ = self.analyze_and_plan(code, src_language=src_language)
        return issues

    def create_specialized_agents(self, issues: List[Issue]) -> List[BaseAgent]:
        """Dynamically create specialized agents based on the issue types.

        This does not run the repairs; it just instantiates appropriate agents.
        """
        specialized_agents: List[BaseAgent] = []
        for issue in issues:
            if issue.type == "syntax_error":
                specialized_agents.append(SyntaxAgent())
            elif issue.type == "logic_bug":
                specialized_agents.append(LogicAgent())
            elif issue.type == "performance_issue":
                specialized_agents.append(OptimizationAgent())
            else:
                # For style or unknown issues, reuse LogicAgent as a generic fixer
                specialized_agents.append(LogicAgent())

        return specialized_agents


# ---------------------------------------------------------------------------
# WEB APP ONLY AGENTS (Not used in dataset evaluation)
# ---------------------------------------------------------------------------

class TestGeneratorAgent(BaseAgent):
    """Agent focused on automatically generating unit tests for repaired code.
    
    **PURPOSE**: Safety & Transparency
    - Automatically generates test cases to verify the repaired code works correctly
    - Provides additional confidence in the repair quality
    - Helps catch edge cases and validate correctness
    
    **WEB APP ONLY**: This agent is designed for interactive use in the web interface
    and is NOT used during dataset evaluation.
    """
    
    def generate_tests(self, code: str, language: str, bug_id: str = None, 
                      num_tests: int = 5) -> dict:
        """Generate unit tests for the given code.
        
        Args:
            code: The repaired code to test
            language: Programming language (Python or Java)
            bug_id: Optional bug identifier for context
            num_tests: Number of test cases to generate (default: 5)
            
        Returns:
            dict with 'test_code', 'test_descriptions', and 'coverage_notes'
        """
        
        # Determine test framework based on language
        if language.lower() == "python":
            test_framework = "pytest"
            test_import = "import pytest"
            test_decorator = "@pytest.mark.parametrize"
        elif language.lower() == "java":
            test_framework = "JUnit 4"
            test_import = "import org.junit.*;\nimport static org.junit.Assert.*;"
            test_decorator = "@Test"
        else:
            test_framework = "standard testing"
            test_import = ""
            test_decorator = ""
        
        prompt = f"""
You are an expert test engineer specialized in {language} testing.

Your task is to generate comprehensive unit tests for the following {language} code to verify its correctness.

**Code to Test:**
```{language}
{code}
```

**Requirements:**
1. Generate {num_tests} diverse test cases that cover:
   - Normal/typical inputs
   - Edge cases (empty inputs, boundary values, etc.)
   - Error/exception handling (if applicable)
   - Different code paths

2. Use {test_framework} testing framework
3. Include clear, descriptive test names
4. Add comments explaining what each test validates
5. Ensure tests are executable and follow best practices{f'''
6. CRITICAL: Test class name should be `{bug_id}_TEST` if the code class is `{bug_id}`
7. Use correct package structure: `package java_testcases.junit;`''' if language.lower() == 'java' and bug_id else ''}

**Output Format (JSON):**
{{
  "test_code": "<complete test code with {num_tests} test methods>",
  "test_descriptions": [
    {{
      "test_name": "test_normal_case",
      "description": "What this test validates",
      "input": "Example input",
      "expected": "Expected output"
    }}
  ],
  "coverage_notes": "Summary of what aspects are covered by these tests",
  "framework": "{test_framework}"
}}

Return ONLY the JSON object, without markdown fences.
"""
        
        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        
        try:
            data = self._extract_json(raw)
        except ValueError:
            logger.warning(f"TestGeneratorAgent: failed to parse JSON response. Raw: {raw[:100]}...")
            return {
                "test_code": f"# Failed to generate tests\n# Raw response: {raw[:200]}...",
                "test_descriptions": [],
                "coverage_notes": "Test generation failed - could not parse response",
                "framework": test_framework
            }
        
        # Clean up test_code if it contains markdown
        test_code = data.get("test_code", "")
        test_code = self._strip_markdown(test_code)
        data["test_code"] = test_code
        
        return data
    
    def execute_tests(self, test_code: str, fixed_code: str, language: str, bug_id: str = None) -> dict:
        """Execute the generated tests and capture results.
        
        Args:
            test_code: The generated test code
            fixed_code: The repaired code to test
            language: Programming language (Python or Java)
            bug_id: Optional bug identifier
            
        Returns:
            dict with 'execution_success', 'test_results', 'output', and 'summary'
        """
        import subprocess
        import tempfile
        import os
        
        results = {
            "execution_success": False,
            "test_results": [],
            "output": "",
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0
            }
        }
        
        try:
            if language.lower() == "python":
                # Execute Python tests with pytest
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Write the fixed code
                    code_file = os.path.join(tmpdir, "repaired_code.py")
                    with open(code_file, "w", encoding="utf-8") as f:
                        f.write(fixed_code)
                    
                    # Write the test code
                    test_file = os.path.join(tmpdir, "test_repaired_code.py")
                    # Inject import of the repaired code into tests
                    test_code_with_import = f"from repaired_code import *\n\n{test_code}"
                    with open(test_file, "w", encoding="utf-8") as f:
                        f.write(test_code_with_import)
                    
                    # Run pytest
                    result = subprocess.run(
                        ["pytest", test_file, "-v", "--tb=short"],
                        capture_output=True,
                        text=True,
                        cwd=tmpdir,
                        timeout=10
                    )
                    
                    results["output"] = result.stdout + "\n" + result.stderr
                    results["execution_success"] = result.returncode == 0
                    
                    # Parse pytest output
                    output_lines = results["output"].split("\n")
                    for line in output_lines:
                        if " PASSED" in line:
                            test_name = line.split("::")[1].split(" ")[0] if "::" in line else "unknown"
                            results["test_results"].append({
                                "name": test_name,
                                "status": "PASSED",
                                "message": ""
                            })
                            results["summary"]["passed"] += 1
                            results["summary"]["total"] += 1
                        elif " FAILED" in line:
                            test_name = line.split("::")[1].split(" ")[0] if "::" in line else "unknown"
                            results["test_results"].append({
                                "name": test_name,
                                "status": "FAILED",
                                "message": "Test assertion failed"
                            })
                            results["summary"]["failed"] += 1
                            results["summary"]["total"] += 1
                        elif " ERROR" in line:
                            test_name = line.split("::")[1].split(" ")[0] if "::" in line else "unknown"
                            results["test_results"].append({
                                "name": test_name,
                                "status": "ERROR",
                                "message": "Test execution error"
                            })
                            results["summary"]["errors"] += 1
                            results["summary"]["total"] += 1
                    
            elif language.lower() == "java":
                # Execute Java tests with JUnit
                # Note: This requires JUnit jars to be available
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                lib_dir = os.path.join(project_root, "lib")
                junit_jar = os.path.join(lib_dir, "junit-4.13.2.jar")
                hamcrest_jar = os.path.join(lib_dir, "hamcrest-core-1.3.jar")
                
                if not os.path.exists(junit_jar):
                    results["output"] = "JUnit jar not found - cannot execute Java tests"
                    return results
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Write the fixed code
                    code_file = os.path.join(tmpdir, f"{bug_id or 'Solution'}.java")
                    with open(code_file, "w", encoding="utf-8") as f:
                        f.write(fixed_code)
                    
                    # Write the test code
                    test_file = os.path.join(tmpdir, f"{bug_id or 'Solution'}_TEST.java")
                    with open(test_file, "w", encoding="utf-8") as f:
                        f.write(test_code)
                    
                    # Compile
                    classpath = f".{os.pathsep}{junit_jar}{os.pathsep}{hamcrest_jar}"
                    compile_result = subprocess.run(
                        ["javac", "-cp", classpath, code_file, test_file],
                        capture_output=True,
                        text=True,
                        cwd=tmpdir,
                        timeout=10
                    )
                    
                    if compile_result.returncode != 0:
                        results["output"] = f"Compilation failed:\n{compile_result.stderr}"
                        return results
                    
                    # Run tests
                    test_class = f"{bug_id or 'Solution'}_TEST"
                    run_result = subprocess.run(
                        ["java", "-cp", f".{os.pathsep}{junit_jar}{os.pathsep}{hamcrest_jar}",
                         "org.junit.runner.JUnitCore", test_class],
                        capture_output=True,
                        text=True,
                        cwd=tmpdir,
                        timeout=10
                    )
                    
                    results["output"] = run_result.stdout + "\n" + run_result.stderr
                    results["execution_success"] = run_result.returncode == 0
                    
                    # Parse JUnit output
                    if "OK " in results["output"]:
                        # All tests passed
                        import re
                        match = re.search(r'OK \((\d+) test', results["output"])
                        if match:
                            num_tests = int(match.group(1))
                            results["summary"]["total"] = num_tests
                            results["summary"]["passed"] = num_tests
                            for i in range(num_tests):
                                results["test_results"].append({
                                    "name": f"test_{i+1}",
                                    "status": "PASSED",
                                    "message": ""
                                })
                    elif "FAILURES!!!" in results["output"]:
                        # Some tests failed
                        import re
                        match = re.search(r'Tests run: (\d+),\s+Failures: (\d+)', results["output"])
                        if match:
                            results["summary"]["total"] = int(match.group(1))
                            results["summary"]["failed"] = int(match.group(2))
                            results["summary"]["passed"] = results["summary"]["total"] - results["summary"]["failed"]
            else:
                results["output"] = f"Unsupported language: {language}"
                
        except subprocess.TimeoutExpired:
            results["output"] = "Test execution timed out (>10 seconds)"
        except Exception as e:
            results["output"] = f"Test execution error: {str(e)}"
            logger.warning(f"TestGeneratorAgent execution failed: {e}")
        
        return results
    
    def validate_repair_with_tests(self, original_code: str, fixed_code: str, 
                                   language: str, bug_id: str = None) -> dict:
        """Generate tests and provide a validation report for the repair.
        
        This method combines test generation with a validation assessment.
        
        Args:
            original_code: The original buggy code
            fixed_code: The repaired code
            language: Programming language
            bug_id: Optional bug identifier
            
        Returns:
            dict with 'tests', 'validation_summary', and 'confidence_score'
        """
        # First generate tests for the fixed code
        tests = self.generate_tests(fixed_code, language, bug_id)
        
        # Execute the generated tests using the RuntimeEvaluationPipeline
        from runtime_evaluator import RuntimeEvaluationPipeline
        pipeline = RuntimeEvaluationPipeline()
        
        # Use the pipeline to evaluate
        eval_result = pipeline.evaluate(
            bug_id=bug_id or "unknown_bug",
            original_code=original_code,
            repaired_code=fixed_code,
            test_code=tests.get('test_code', ''),
            language=language
        )
        
        execution_results = eval_result["execution"]
        
        # Then generate a validation summary
        prompt = f"""
You are a code quality expert.

Compare the original buggy code with the fixed code, considering the generated tests.

**Original Code:**
```{language}
{original_code}
```

**Fixed Code:**
```{language}
{fixed_code}
```

**Generated Tests:**
```{language}
{tests.get('test_code', '')}
```


**Test Execution Results:**
Error Analysis: {eval_result.get('failure_analysis', {})}
{execution_results}

**Your Task:**
1. Assess whether the generated tests adequately validate the fix
2. Identify any missing test cases or edge cases not covered
3. Assign a confidence score (0-100) for the repair quality based on:
   - How well the fix addresses the original bug
   - Test coverage completeness
   - Potential remaining issues

**Output Format (JSON):**
{{
  "validation_summary": "Brief assessment of the repair and test coverage",
  "confidence_score": 85,
  "missing_tests": ["Any important test cases that should be added"],
  "concerns": ["Any remaining issues or risks"]
}}

Return ONLY the JSON object.
"""
        
        raw = call_llm(self.model_name, prompt, temp=0.3)
        
        try:
            validation = self._extract_json(raw)
        except ValueError:
            validation = {
                "validation_summary": "Could not generate validation assessment",
                "confidence_score": 50,
                "missing_tests": [],
                "concerns": ["Validation failed to parse"]
            }
        
        return {
            "tests": tests,
            "validation": validation,
            "execution": execution_results,
            "analysis": eval_result.get("failure_analysis", {}),
            "hallucinations": eval_result.get("hallucinations", [])
        }


if __name__ == "__main__":
    # Simple manual tests for Subtask 1 & 2 when running this file directly.
    logging.basicConfig(level=logging.INFO)

    sample_buggy_code = """
def add_numbers(a, b)
    # Missing colon above, and wrong return below
    result = a - b
    return result
"""

    main_agent = MainAgent()
    print("=== Running MainAgent analysis+plan on sample buggy code ===")
    issues, plan = main_agent.analyze_and_plan(sample_buggy_code, src_language="Python")
    print(f"Plan: translate={plan.translate}, target_language={plan.target_language}")
    for issue in issues:
        print(f"- Issue {issue.id}: type={issue.type}, location={issue.location_hint}")
        print(f"  Description: {issue.description}")

    if issues:
        print("\\n=== Testing specialized agents on the first issue ===")
        first_issue = issues[0]
        agents_for_issues = main_agent.create_specialized_agents([first_issue])
        specialized_agent = agents_for_issues[0]
        repair_result = specialized_agent.repair(sample_buggy_code, first_issue, "Python")

        print("\\n--- Fixed Code ---")
        print(repair_result.fixed_code)
        print("\\n--- Explanation ---")
        print(repair_result.explanation)
