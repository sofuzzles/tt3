from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import Question, Tag, User, Answer

def index(request):
	latest_question_list = Question.objects.order_by('-created_at')[:5]
	try:
		exp_question = Question.objects.get(pk=request.GET['responses_requested'])
		expanded_question_list = [exp_question]
	except (KeyError, Question.DoesNotExist):
		expanded_question_list = []
	
	template = loader.get_template('blog/index.html')
	context = {
		'latest_question_list' : latest_question_list,
		'expanded_question_list' : expanded_question_list, 
	}
	return HttpResponse(template.render(context, request))
	
def update(request):
	q = request.POST['question']
	anon_user = User.objects.all()[0]
	question = Question(text=q, user=anon_user, created_at=timezone.now())
	question.save()
	
	return HttpResponseRedirect(reverse("index"))