import os
import json
import logging
from dataclasses import dataclass
from typing import List, Literal, Optional

import yaml
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time


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


def _configure_genai() -> None:
    """Configure Gemini using API key from environment.

    Expected env var: GEMINI_API_KEY
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please export GEMINI_API_KEY with your Gemini API key."
        )
    genai.configure(api_key=api_key)


def call_llm(model_name: str, prompt: str, temp: float = 0.2) -> str:
    """Lightweight wrapper around the Gemini text-generation API.

    This is shared by legacy functions and the new agent classes.
    """
    _configure_genai()
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=temp),
        )
        text = getattr(response, "text", "") or ""
        return text
    except Exception as e:
        logger.error(f"Error calling LLM model '{model_name}': {e}")
        raise

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
        """
        return call_llm(model_name, prompt)

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

    def repair(self, code: str, issue: Issue, language: str) -> RepairResult:
        """Subclasses must implement this to perform the actual repair."""
        raise NotImplementedError


class SyntaxAgent(BaseAgent):
    """Agent focused on resolving syntax and parsing errors."""

    def repair(self, code: str, issue: Issue, language: str) -> RepairResult:
        prompt = f"""
        You are an expert {language} compiler and code fixer.

        Your task is to fix ONLY the syntax or parsing issues in the following {language} code.

        Issue description:
        {issue.description}

        Current code:
        ```{language}
        {code}
        ```

        Requirements:
        - Return valid, executable {language} code that is syntactically correct.
        - Do NOT change the overall logic beyond what is required to fix syntax.
        - After the code, provide a short explanation (2–4 sentences) of what you changed and why.

        Output format (JSON):
        {{
          "fixed_code": "<fixed {language} code>",
          "explanation": "<short explanation of the changes>"
        }}

        Return ONLY the JSON object, without any markdown fences.
        """
        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: if the model did not respect JSON, return original code with explanation
            logger.warning("SyntaxAgent: failed to parse JSON response; returning original code.")
            return RepairResult(
                fixed_code=code,
                explanation=f"Failed to parse model response as JSON. Raw response: {raw}",
            )

        return RepairResult(
            fixed_code=data.get("fixed_code", code),
            explanation=data.get("explanation", "No explanation provided by the model."),
        )


class LogicAgent(BaseAgent):
    """Agent focused on fixing logical/semantic bugs."""

    def repair(self, code: str, issue: Issue, language: str) -> RepairResult:
        prompt = f"""
        You are an expert {language} software engineer.

        The following {language} code has a LOGICAL or SEMANTIC bug, not just syntax.

        Issue description:
        {issue.description}

        Buggy code:
        ```{language}
        {code}
        ```

        Tasks:
        1. Correct the logic so the code behaves as intended.
        2. Preserve the overall structure and style as much as possible.

        Output format (JSON):
        {{
          "fixed_code": "<corrected {language} code>",
          "explanation": "<short explanation of what was wrong and how you fixed it>"
        }}

        Return ONLY the JSON object, without any markdown.
        """
        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("LogicAgent: failed to parse JSON response; returning original code.")
            return RepairResult(
                fixed_code=code,
                explanation=f"Failed to parse model response as JSON. Raw response: {raw}",
            )

        return RepairResult(
            fixed_code=data.get("fixed_code", code),
            explanation=data.get("explanation", "No explanation provided by the model."),
        )


class OptimizationAgent(BaseAgent):
    """Agent focused on performance and efficiency improvements."""

    def repair(self, code: str, issue: Issue, language: str) -> RepairResult:
        prompt = f"""
        You are an expert {language} performance engineer.

        Optimize the following {language} code for better performance and/or memory efficiency,
        while preserving its external behavior.

        Performance issue description:
        {issue.description}

        Original code:
        ```{language}
        {code}
        ```

        Requirements:
        - Keep the code readable and idiomatic.
        - Explain the key optimization ideas.

        Output format (JSON):
        {{
          "fixed_code": "<optimized {language} code>",
          "explanation": "<short explanation of the optimizations>"
        }}

        Return ONLY the JSON object, without any markdown.
        """
        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("OptimizationAgent: failed to parse JSON response; returning original code.")
            return RepairResult(
                fixed_code=code,
                explanation=f"Failed to parse model response as JSON. Raw response: {raw}",
            )

        return RepairResult(
            fixed_code=data.get("fixed_code", code),
            explanation=data.get("explanation", "No explanation provided by the model."),
        )


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
                logger.warning(f"MainAgent: skipping malformed issue entry {item}: {e}")
        return issues

    def analyze_and_plan(self, code: str, src_language: str = "Python") -> tuple[List[Issue], RepairPlan]:
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

        prompt = f"""
        {system_instructions}

        Original language of the code: {src_language}

        Here is the code to analyze:
        ```
        {code}
        ```
        """

        raw = call_llm(self.model_name, prompt, temp=self.temperature)
        cleaned = raw.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error("MainAgent: failed to parse JSON from analysis+plan response.")
            logger.debug(f"Raw response: {raw}")
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

