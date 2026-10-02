from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Lesson, Question, Choice, Submission, Enrollment

def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=user, course=course)
    
    submission = Submission.objects.create(enrollment=enrollment)
    
    selected_choice_ids = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            selected_choice_ids.append(int(value))
            
    for choice_id in selected_choice_ids:
        choice = get_object_or_404(Choice, pk=choice_id)
        submission.choices.add(choice)
        
    submission.save()
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_ids = [choice.id for choice in submission.choices.all()]
    
    total_score = 0
    total_possible = 0
    
    for question in course.question_set.all():
        total_possible += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    score_percentage = int((total_score / total_possible) * 100) if total_possible > 0 else 0
    passed = score_percentage >= 70

    context['course'] = course
    context['submission'] = submission
    context['grade'] = score_percentage
    context['passed'] = passed
    context['selected_ids'] = selected_ids
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)