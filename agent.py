"""
Developer Error Interpreter Agent using Google ADK and Gemini.
"""

import json
import asyncio
import os
from google import genai
from google.genai import types
from typing import Optional
from schemas import AnalyzeResponse, FixStep


class ErrorInterpreterAgent:
    """
    A single agent that analyzes developer errors and returns structured explanations.
    """
    
    SYSTEM_PROMPT = """You are an expert developer error interpreter. Your role is to analyze terminal errors and exception messages, then provide clear, structured explanations and fixes.

When analyzing errors:
1. Identify the error type and what went wrong
2. Explain the probable cause in simple terms
3. Provide step-by-step fix instructions
4. Suggest shell commands if applicable
5. Rate your confidence in the diagnosis (low/medium/high)
6. Add any important caveats

Always respond with valid JSON matching this exact schema:
{
    "error_summary": "Plain English explanation of what the error means",
    "probable_cause": "The root cause of this error",
    "fix_steps": [
        {"step": 1, "action": "First action to resolve the error"},
        {"step": 2, "action": "Second action to resolve the error"}
    ],
    "commands": ["optional_command_1", "optional_command_2"],
    "confidence": "high|medium|low",
    "notes": "Optional caveats or additional context"
}"""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize the agent with Gemini API key.
        
        Args:
            api_key: Google API key for Gemini
            model: Optional model name override. Can be either a short name like
                   "gemini-2.5-flash" or a full resource name like
                   "models/gemini-2.5-flash".
        """
        self.client = genai.Client(api_key=api_key)
        self.model = self._select_model(model)

    @staticmethod
    def _normalize_model_name(model: Optional[str]) -> Optional[str]:
        if not model:
            return None
        model = model.strip()
        if not model:
            return None
        if model.startswith("models/"):
            return model
        return f"models/{model}"

    def _select_model(self, model_override: Optional[str]) -> str:
        env_model = os.getenv("GEMINI_MODEL")
        requested = self._normalize_model_name(model_override or env_model)

        try:
            models = list(self.client.models.list(config={"page_size": 200}))
        except Exception as e:
            if requested:
                return requested
            raise RuntimeError(
                "Unable to list available Gemini models. "
                "Set GEMINI_MODEL to a valid model name (e.g. models/gemini-2.5-flash). "
                f"Underlying error: {e}"
            )

        generate_models = [
            m.name for m in models
            if getattr(m, "name", None) and ("generateContent" in (m.supported_actions or []))
        ]
        if not generate_models:
            if requested:
                return requested
            raise RuntimeError(
                "No Gemini models available for generateContent with this API key. "
                "Set GEMINI_MODEL to a model you have access to."
            )

        if requested:
            return requested

        preferred = [
            "models/gemini-2.5-flash",
            "models/gemini-flash-latest",
            "models/gemini-2.0-flash",
            "models/gemini-pro-latest",
        ]
        for candidate in preferred:
            if candidate in generate_models:
                return candidate
        return generate_models[0]

    async def analyze(self, error_text: str) -> AnalyzeResponse:
        """Async wrapper used by the FastAPI handler."""
        return await asyncio.to_thread(self.analyze_error, error_text)
    
    def analyze_error(self, error_text: str) -> AnalyzeResponse:
        """
        Analyze a developer error and return structured explanation and fixes.
        
        Args:
            error_text: The error message or terminal output to analyze
            
        Returns:
            AnalyzeResponse: Structured error analysis with fixes
            
        Raises:
            ValueError: If analysis fails or returns invalid JSON
        """
        if not error_text or not error_text.strip():
            raise ValueError("Error text cannot be empty")
        
        user_message = f"""Please analyze this developer error and provide a structured explanation with fix steps:

Error:
{error_text}"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_PROMPT,
                    temperature=0.2,
                    max_output_tokens=1200,
                    response_mime_type="application/json",
                ),
            )
            
            # Extract the response text
            response_text = response.text
            if not response_text:
                raise ValueError("Model returned an empty response")
            
            # Parse JSON from response
            try:
                try:
                    analysis_data = json.loads(response_text)
                except json.JSONDecodeError:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        analysis_data = json.loads(json_str)
                    else:
                        raise ValueError("No JSON found in response")
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON response: {str(e)}")
            
            # Convert fix_steps list to FixStep objects
            fix_steps = []
            for step in analysis_data.get("fix_steps", []):
                if isinstance(step, dict):
                    fix_steps.append(FixStep(step_number=len(fix_steps)+1, action=step.get("action", "")))
            
            # Create and return the response
            return AnalyzeResponse(
                error_summary=analysis_data.get("error_summary", ""),
                probable_cause=analysis_data.get("probable_cause", ""),
                fix_steps=fix_steps,
                commands=analysis_data.get("commands", []),
                confidence=analysis_data.get("confidence", "medium"),
                notes=analysis_data.get("notes")
            )
            
        except Exception as e:
            raise ValueError(f"Error analyzing text: {str(e)}")
