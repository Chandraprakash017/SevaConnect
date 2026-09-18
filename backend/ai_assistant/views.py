"""
AI Assistant views for SevaConnect.

Two-step AI diagnosis flow:
  Step 1: Customer describes problem → AI returns initial assessment + follow-up questions
  Step 2: Customer answers questions → AI gives refined diagnosis

The diagnosis is stored in the ai_diagnosis collection and linked to bookings.
"""

from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from common.db import db
from common.utils import serialize_doc, str_to_objectid
from ai_assistant.ai_service import get_initial_diagnosis, get_followup_diagnosis, get_chat_response


@api_view(['POST'])
@permission_classes([AllowAny])
def diagnose(request):
    """
    Step 1: Customer describes their problem.

    The AI returns an initial assessment and 2-3 follow-up questions
    to better understand the issue.

    Request body:
    {
        "problem": "My bike is not starting, self makes a clicking sound"
    }

    Response includes a session_id that must be passed to /followup/ endpoint.
    """
    problem = request.data.get('problem', '').strip()

    if not problem:
        return Response({"error": "'problem' is required."}, status=status.HTTP_400_BAD_REQUEST)

    if len(problem) > 1000:
        return Response({"error": "Problem description too long (max 1000 characters)."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Call Gemini AI to get initial diagnosis
        ai_result = get_initial_diagnosis(problem)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception:
        return Response(
            {"error": "Unable to process the problem right now. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Save the diagnosis session to MongoDB so we can continue in step 2
    diagnosis_doc = {
        "problem_description": problem,
        "initial_diagnosis": ai_result,
        "follow_up_answers": [],
        "final_diagnosis": None,
        "status": "pending_followup",    # pending_followup | complete
        "created_at": datetime.utcnow(),
    }

    result = db.ai_diagnosis.insert_one(diagnosis_doc)
    session_id = str(result.inserted_id)

    return Response({
        "session_id": session_id,
        "problem": problem,
        "initial_diagnosis": ai_result,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def followup(request):
    """
    Step 2: Customer submits answers to the follow-up questions.

    The AI uses the original problem + answers to give a more specific diagnosis.

    Request body:
    {
        "session_id": "<id from step 1>",
        "answers": [
            {"question": "Does the horn work?", "answer": "Yes"},
            {"question": "Does the self make any sound?", "answer": "Yes, clicking sound"},
            {"question": "Did this happen suddenly?", "answer": "Yes"}
        ]
    }
    """
    session_id = request.data.get('session_id', '').strip()
    answers = request.data.get('answers', [])

    if not session_id:
        return Response({"error": "'session_id' is required."}, status=status.HTTP_400_BAD_REQUEST)

    if not answers:
        return Response({"error": "'answers' list is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Find the diagnosis session
    session = db.ai_diagnosis.find_one({"_id": str_to_objectid(session_id)})
    if not session:
        return Response({"error": "Diagnosis session not found."}, status=status.HTTP_404_NOT_FOUND)

    problem = session['problem_description']

    try:
        # Get refined diagnosis based on the answers
        final_diagnosis = get_followup_diagnosis(problem, answers)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception:
        return Response(
            {"error": "Unable to process the answers right now. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Update the session with the final diagnosis
    db.ai_diagnosis.update_one(
        {"_id": str_to_objectid(session_id)},
        {"$set": {
            "follow_up_answers": answers,
            "final_diagnosis": final_diagnosis,
            "status": "complete",
            "completed_at": datetime.utcnow(),
        }}
    )

    return Response({
        "session_id": session_id,
        "problem": problem,
        "final_diagnosis": final_diagnosis,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_diagnosis_session(request, session_id):
    """Get a stored AI diagnosis session (used when creating a booking)."""
    session = db.ai_diagnosis.find_one({"_id": str_to_objectid(session_id)})
    if not session:
        return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(serialize_doc(session))


@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    """
    General AI chat assistant for the help page.

    Request body:
    {
        "message": "What services do you offer for AC repair?",
        "history": [...]  (optional - previous messages for context)
    }
    """
    message = request.data.get('message', '').strip()
    history = request.data.get('history', [])

    if not message:
        return Response({"error": "'message' is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reply = get_chat_response(message, history)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception:
        return Response(
            {"error": "Chat service unavailable right now."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Add this turn to the history for the frontend to track
    updated_history = [
        *history,
        {"role": "user", "parts": [message]},
        {"role": "model", "parts": [reply]},
    ]

    return Response({
        "reply": reply,
        "history": updated_history,
    })
