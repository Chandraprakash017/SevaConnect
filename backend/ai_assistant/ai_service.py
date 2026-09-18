"""
AI Service module for SevaConnect.

This module handles all the logic for calling the Gemini API.
It is used by ai_assistant/views.py.

Keeping the API logic here (separate from views) makes the code cleaner.
"""

import json
import re
from django.conf import settings
from ai_assistant.prompts import INITIAL_DIAGNOSIS_PROMPT, FOLLOWUP_DIAGNOSIS_PROMPT, CHAT_SYSTEM_PROMPT


def _get_gemini_client():
    """Create and return a Gemini API client."""
    try:
        # Try the newer google-genai SDK first
        from google import genai
        return genai.Client(api_key=settings.GEMINI_API_KEY), "new"
    except ImportError:
        # Fall back to the older google-generativeai SDK
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai, "old"


def _extract_json(text):
    """
    Extract JSON from AI response text.
    Sometimes Gemini wraps JSON in markdown code blocks, so we strip those.
    """
    # Remove markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```[a-z]*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)

    # Try to parse the JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # If JSON parsing fails, try to find JSON within the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                return None
    return None


def get_initial_diagnosis(problem_description):
    """
    Step 1 of AI flow: Customer describes problem, AI returns initial assessment.

    Returns a dict with:
    - problem_summary
    - category
    - possible_causes
    - recommended_service
    - confidence
    - follow_up_questions
    - preliminary_note

    Raises an exception if the API call fails.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")

    prompt_text = f"Customer Problem: {problem_description}"

    client, sdk_version = _get_gemini_client()

    if sdk_version == "new":
        from google.genai import types as genai_types
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_text,
            config=genai_types.GenerateContentConfig(
                system_instruction=INITIAL_DIAGNOSIS_PROMPT,
                max_output_tokens=800,
                temperature=0.3,   # Low temperature for consistent structured output
            )
        )
        response_text = response.text
    else:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = client.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=INITIAL_DIAGNOSIS_PROMPT,
            )
            response = model.generate_content(prompt_text)
            response_text = response.text

    # Parse the JSON response
    result = _extract_json(response_text)

    if not result:
        # If we can't parse JSON, return a safe fallback
        raise ValueError(f"AI returned unexpected format. Raw: {response_text[:200]}")

    return result


def get_followup_diagnosis(problem_description, questions_and_answers):
    """
    Step 2 of AI flow: After customer answers follow-up questions, get refined diagnosis.

    questions_and_answers is a list of:
    [{"question": "Does the horn work?", "answer": "Yes"}]

    Returns a dict with refined diagnosis.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    # Build a clear prompt with the original problem + answers
    qa_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in questions_and_answers])
    prompt_text = f"Original Problem: {problem_description}\n\nFollow-up Answers:\n{qa_text}"

    client, sdk_version = _get_gemini_client()

    if sdk_version == "new":
        from google.genai import types as genai_types
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_text,
            config=genai_types.GenerateContentConfig(
                system_instruction=FOLLOWUP_DIAGNOSIS_PROMPT,
                max_output_tokens=800,
                temperature=0.3,
            )
        )
        response_text = response.text
    else:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = client.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=FOLLOWUP_DIAGNOSIS_PROMPT,
            )
            response = model.generate_content(prompt_text)
            response_text = response.text

    result = _extract_json(response_text)

    if not result:
        raise ValueError(f"AI returned unexpected format. Raw: {response_text[:200]}")

    return result


def get_chat_response(message, history=None):
    """
    General AI chat for the help chatbot.
    history is a list of {"role": "user"/"model", "parts": ["text"]}
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    client, sdk_version = _get_gemini_client()

    if sdk_version == "new":
        from google.genai import types as genai_types
        contents = []
        if history:
            for h in history:
                contents.append(
                    genai_types.Content(
                        role=h['role'],
                        parts=[genai_types.Part(text=h['parts'][0])]
                    )
                )
        contents.append(
            genai_types.Content(role="user", parts=[genai_types.Part(text=message)])
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=genai_types.GenerateContentConfig(
                system_instruction=CHAT_SYSTEM_PROMPT,
                max_output_tokens=500,
                temperature=0.5,
            )
        )
        return response.text
    else:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = client.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=CHAT_SYSTEM_PROMPT,
            )
            if history:
                chat = model.start_chat(history=history)
                response = chat.send_message(message)
            else:
                response = model.generate_content(message)
            return response.text
