from django.urls import path
from . import views

urlpatterns = [
    # path('', view=views.Question.as_view(), name='question'),
    path('exam/', views.exam_view, name='exam'),
    path('upload_questions/', views.upload_questions, name='upload_questions'),

]
