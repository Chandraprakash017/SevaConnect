"""
AI Assistant views for SevaConnect.

Uses Google Gemini to diagnose appliance/home problems described by the user
and recommend the appropriate service category.

This is a core feature of SevaConnect — users describe their problem in plain
language and the AI helps them find the right service.
"""

import google.generativeai as genai
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status


# Configure the Gemini client once at module load time
genai.configure(api_key=settings.GEMINI_API_KEY)


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


@api_view(['POST'])
@permission_classes([AllowAny])
def diagnose(request):
    """
    AI diagnosis endpoint.

    Accepts a problem description from the user and returns AI-generated
    diagnosis, recommended service, and first-aid steps.

    Expected body:
    {
        "problem": "My AC is making a loud rattling noise and not cooling",
        "language": "en"   (optional, default "en")
    }
    """
    problem = request.data.get('problem', '').strip()

    if not problem:
        return Response({"error": "'problem' description is required."}, status=status.HTTP_400_BAD_REQUEST)

    if len(problem) > 1000:
        return Response({"error": "Problem description is too long (max 1000 chars)."}, status=status.HTTP_400_BAD_REQUEST)

    if not settings.GEMINI_API_KEY:
        return Response(
            {"error": "AI service is not configured. Please contact support."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=DIAGNOSIS_SYSTEM_PROMPT,
        )

        response = model.generate_content(
            f"User's problem: {problem}",
            generation_config=genai.GenerationConfig(
                max_output_tokens=600,
                temperature=0.4,   # Lower temperature = more factual, less creative
            )
        )

        ai_response = response.text

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
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=DIAGNOSIS_SYSTEM_PROMPT,
        )

        # Start a chat session with the provided history
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(
            message,
            generation_config=genai.GenerationConfig(
                max_output_tokens=500,
                temperature=0.4,
            )
        )

        # Return updated history so frontend can maintain conversation state
        updated_history = [
            *history,
            {"role": "user", "parts": [message]},
            {"role": "model", "parts": [response.text]},
        ]

    except Exception as e:
        return Response(
            {"error": f"AI service error: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY
        )

    return Response({
        "reply": response.text,
        "history": updated_history,
    })
