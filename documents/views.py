from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import Document
import os


@login_required
def document_list(request):
    documents = Document.objects.select_related('uploaded_by').order_by('-created_at')

    category = request.GET.get('category')
    if category:
        documents = documents.filter(category=category)

    search = request.GET.get('search', '')
    if search:
        documents = documents.filter(title__icontains=search)

    context = {
        'documents':  documents,
        'total':      Document.objects.count(),
        'general':    Document.objects.filter(category='general').count(),
        'policy':     Document.objects.filter(category='policy').count(),
        'other':      Document.objects.exclude(category__in=['general', 'policy']).count(),
        'selected_category': category or '',
        'search': search,
        'categories': Document.CATEGORY_CHOICES,
    }
    return render(request, 'documents/document_list.html', context)


@login_required
def document_upload(request):
    if request.method == 'POST':
        title       = request.POST.get('title', '')
        description = request.POST.get('description', '')
        category    = request.POST.get('category', 'general')
        file        = request.FILES.get('file')

        if not title or not file:
            messages.error(request, 'Title and file are required.')
            return redirect('document_upload')

        Document.objects.create(
            title=title,
            description=description,
            category=category,
            file=file,
            uploaded_by=request.user,
        )
        messages.success(request, f'Document "{title}" uploaded successfully!')
        return redirect('document_list')

    return render(request, 'documents/document_upload.html')


@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        # Delete the actual file
        if doc.file and os.path.exists(doc.file.path):
            os.remove(doc.file.path)
        title = doc.title
        doc.delete()
        messages.success(request, f'Document "{title}" deleted.')
    return redirect('document_list')


@login_required
def document_summarize(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            content = document.description or f"Document titled: {document.title}"

            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=400,
                system="You are a document analyst. Summarize business documents clearly and extract key points.",
                messages=[{
                    'role': 'user',
                    'content': f"Summarize this document:\nTitle: {document.title}\nCategory: {document.category}\nDescription: {content}"
                }],
            )
            summary = response.content[0].text
            document.ai_summary = summary
            document.save()
            return JsonResponse({'summary': summary})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POST required'}, status=405)