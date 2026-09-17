"""
AI Assistant views for SevaConnect.

Uses Google Gemini to diagnose appliance/home problems described by the user
and recommend the appropriate service category.

This is a core feature of SevaConnect — users describe their problem in plain
language and the AI helps them find the right service.
"""

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_SDK = "new"
except ImportError:
    try:
        import google.generativeai as genai
        GENAI_SDK = "old"
    except ImportError:
        genai = None
        GENAI_SDK = None


DIAGNOSIS_SYSTEM_PROMPT = """You are SevaConnect's AI assistant — a helpful home services expert.

When a user describes a problem with their home appliance, vehicle, or any household issue,
you should:
1. Identify the most likely cause(s) of the problem
2. Estimate the severity (low / medium / high)
3. Recommend which service category they need (e.g., Electrical, Plumbing, AC Repair, Carpentry, Vehicle, etc.)
4. Provide 2-3 practical first-aid steps the user can try before the technician arrives
5. Mention any safety warnings if applicable

Be concise, friendly, and practical. Format your response in clear sections.
Always end with: "Book a verified SevaConnect technician to fix this properly."
"""


def _call_gemini(prompt, system_prompt=None, history=None):
    """
    Unified helper to call Gemini using whichever SDK is available.
    Returns the response text string.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    if GENAI_SDK == "new":
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        contents = []
        if history:
            for h in history:
                role = h.get("role", "user")
                parts_text = h.get("parts", [""])
                contents.append(
                    genai_types.Content(role=role, parts=[genai_types.Part(text=parts_text[0])])
                )
        contents.append(
            genai_types.Content(role="user", parts=[genai_types.Part(text=prompt)])
        )

        config = genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=600,
            temperature=0.4,
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
        )
        return response.text

    elif GENAI_SDK == "old":
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_prompt,
            )
            if history:
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
            else:
                response = model.generate_content(prompt)
            return response.text

    else:
        raise ImportError("No Gemini SDK found. Install: pip install google-genai")


@api_view(['POST'])
@permission_classes([AllowAny])
def diagnose(request):
    """
    AI diagnosis endpoint.

    Accepts a problem description from the user and returns AI-generated
    diagnosis, recommended service, and first-aid steps.

    Expected body:
    {
        "problem": "My AC is making a loud rattling noise and not cooling"
    }
    """
    problem = request.data.get('problem', '').strip()

    if not problem:
        return Response({"error": "'problem' description is required."}, status=status.HTTP_400_BAD_REQUEST)

    if len(problem) > 1000:
        return Response({"error": "Problem description is too long (max 1000 chars)."}, status=status.HTTP_400_BAD_REQUEST)

    if not settings.GEMINI_API_KEY:
        return Response(
            {"error": "AI service is not configured. Please set GEMINI_API_KEY in .env"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    try:
        ai_response = _call_gemini(problem, system_prompt=DIAGNOSIS_SYSTEM_PROMPT)
    except Exception as e:
        return Response(
            {"error": f"AI service error: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    return Response({
        "problem": problem,
        "diagnosis": ai_response,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    """
    Multi-turn AI chat for more conversational problem solving.

    Expected body:
    {
        "message": "The rattling started after I cleaned the filter",
        "history": [
            {"role": "user", "parts": ["My AC is making noise"]},
            {"role": "model", "parts": ["It could be a loose component..."]}
        ]
    }
    """
    message = request.data.get('message', '').strip()
    history = request.data.get('history', [])

    if not message:
        return Response({"error": "'message' is required."}, status=status.HTTP_400_BAD_REQUEST)

    if not settings.GEMINI_API_KEY:
        return Response(
            {"error": "AI service is not configured."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    try:
        reply = _call_gemini(message, system_prompt=DIAGNOSIS_SYSTEM_PROMPT, history=history)
    except Exception as e:
        return Response(
            {"error": f"AI service error: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    updated_history = [
        *history,
        {"role": "user", "parts": [message]},
        {"role": "model", "parts": [reply]},
    ]

    return Response({
        "reply": reply,
        "history": updated_history,
    })
