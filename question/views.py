from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Question as QuestionModel
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from docx import Document
import re
import random
from .models import Answer, Explanation
import json


# Create your views here.
class QuestionView(APIView):
    def get(self, request):
        return Response({"data": 1})
    
# def exam_view(request):
#     if request.method == 'POST':
#         # Handle the form submission
#         submitted_answers = request.POST
#         results = []
#         questions = QuestionModel.objects.all();
#         for question in questions:
#             selected_answer_id = submitted_answers.get(str(question.id))
#             selected_answer = question.answers.get(id=selected_answer_id)
#             correct_answer = question.answers.filter(is_correct=True).first()
#             results.append({
#                 'question': question,
#                 'selected_answer': selected_answer,
#                 'correct_answer': correct_answer,
#                 'is_correct': selected_answer == correct_answer,
#                 'explanation': question.explanation,
#             })
#         return render(request, 'question/results.html', {'results': results})
#     else:
#         questions = QuestionModel.objects.all()
#         return render(request, 'question/exam.html', {'questions': questions})
def exam_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        question_id = body.get('question_id')
        selected_answer_id = body.get('answer_id')
        question = get_object_or_404(QuestionModel, id=question_id)
        selected_answer = get_object_or_404(Answer, id=selected_answer_id)
        correct_answer = question.answers.filter(is_correct=True).first()
        explanation = question.explanation
        
        result = {
            'question': question.text,
            'selected_answer': selected_answer.text,
            'correct_answer': correct_answer.text,
            'is_correct': selected_answer == correct_answer,
            'explanation': explanation.text,
        }
        return JsonResponse(result)
    else:
        questions = list(QuestionModel.objects.all())
        random.shuffle(questions)
        selected_questions = questions[:30]
        return render(request, 'question/exam.html', {'questions': selected_questions})
    
@csrf_exempt
def upload_questions(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_path = default_storage.save(file.name, file)
        
        document = Document(file_path)
        question_pattern = re.compile(r'### (\d+)\. (.+)')
        answer_pattern = re.compile(r'[a-d]\. (.+)')
        correct_answer_pattern = re.compile(r'\*\*Correct Answer: ([a-d])\. (.+)\*\*')
        explanation_pattern = re.compile(r'\*\*Explanation:\*\* (.+)')

        current_question = None

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if question_pattern.match(text):
                match = question_pattern.match(text)
                question_text = match.group(2)
                current_question = QuestionModel.objects.create(text=question_text)
            elif answer_pattern.match(text) and current_question:
                match = answer_pattern.match(text)
                answer_text = match.group(1)
                is_correct = False
                Answer.objects.create(question=current_question, text=answer_text, is_correct=is_correct)
            elif correct_answer_pattern.match(text) and current_question:
                match = correct_answer_pattern.match(text)
                correct_answer_letter = match.group(1)
                correct_answer_text = match.group(2)
                correct_answer = Answer.objects.get(question=current_question, text=correct_answer_text)
                correct_answer.is_correct = True
                correct_answer.save()
            elif explanation_pattern.match(text) and current_question:
                match = explanation_pattern.match(text)
                explanation_text = match.group(1)
                Explanation.objects.create(question=current_question, text=explanation_text)

        return render(request, 'question/upload.html', {'status': 'success', 'message': 'Questions imported successfully'})
    return render(request, 'question/upload.html')