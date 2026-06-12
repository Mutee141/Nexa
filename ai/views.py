from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from documents.models import Document
import g4f

# Use g4f directly instead of OpenAI to automatically use free providers and avoid quota issues



@login_required
def assistant(request):
    quick_prompts = []  # We handle these in the template directly
    return render(request, 'ai/assistant.html', {'quick_prompts': quick_prompts})


@login_required
def chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data       = json.loads(request.body)
        user_msg   = data.get('message', '').strip()
        history    = data.get('history', [])

        if not user_msg:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": (
                    "You are NexaOps AI Assistant — a smart, helpful business operations assistant. "
                    "You help teams with tasks, projects, meetings, emails, reports, and general business questions. "
                    "Be concise, professional, and practical. Format responses clearly using bullet points or numbered lists when appropriate."
                )
            }
        ]

        # Add conversation history (last 10 messages)
        for msg in history[-10:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Add current message
        messages.append({"role": "user", "content": user_msg})

        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=messages,
        )

        reply = response
        return JsonResponse({'reply': reply})

    except Exception as e:
        return JsonResponse({'error': 'Service is currently busy or unavailable. Please try again in a few moments.'}, status=500)


@login_required
def email_writer(request):
    result = None
    if request.method == 'POST':
        purpose   = request.POST.get('purpose', '')
        recipient = request.POST.get('recipient', '')
        tone      = request.POST.get('tone', 'professional')
        details   = request.POST.get('details', '')

        prompt = (
            f"Write a {tone} business email.\n"
            f"Purpose: {purpose}\n"
            f"Recipient: {recipient}\n"
            f"Key details: {details}\n\n"
            f"Write a complete email with subject line, greeting, body, and sign-off. "
            f"Format: start with 'Subject: ...' on the first line."
        )

        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[
                    {"role": "system", "content": "You are a professional business email writer."},
                    {"role": "user",   "content": prompt}
                ]
            )
            result = response
        except Exception as e:
            result = "We're experiencing high demand right now or a service disruption. Please try again in a few moments."

    return render(request, 'ai/email_writer.html', {'result': result})


@login_required
def task_generator(request):
    result = None
    if request.method == 'POST':
        goal    = request.POST.get('goal', '')
        context = request.POST.get('context', '')

        prompt = (
            f"Break down this business goal into specific, actionable tasks.\n"
            f"Goal: {goal}\n"
            f"Context: {context}\n\n"
            f"Return a numbered list of 5-8 specific tasks. "
            f"For each task include: task name, priority (High/Medium/Low), and estimated time."
        )

        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[
                    {"role": "system", "content": "You are a professional project manager who breaks down goals into actionable tasks."},
                    {"role": "user",   "content": prompt}
                ]
            )
            result = response
        except Exception as e:
            result = "We're experiencing high demand right now or a service disruption. Please try again in a few moments."

    return render(request, 'ai/task_generator.html', {'result': result})


@login_required
def summarize_doc(request, doc_id):
    document = get_object_or_404(Document, pk=doc_id)

    if request.method == 'POST':
        try:
            # Read up to 3000 chars from the document description as sample
            content = document.description or document.title

            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                messages=[
                    {"role": "system", "content": "You are a document analyst. Summarize business documents clearly and concisely."},
                    {"role": "user",   "content": f"Summarize this document:\nTitle: {document.title}\nContent: {content}"}
                ]
            )
            summary = response
            document.ai_summary = summary
            document.save()
            return JsonResponse({'summary': summary})
        except Exception as e:
            return JsonResponse({'error': "We're experiencing high demand right now. Please try again in a few moments."}, status=500)

    return JsonResponse({'error': 'POST required'}, status=405)