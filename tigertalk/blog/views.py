from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from el_pagination.views import AjaxListView
from el_pagination import utils

from .models import Question, Tag, Profile, Answer

def index(request):
	questions = Question.objects.order_by('-created_at')
	user = request.user
	try:
		exp_question = Question.objects.get(pk=request.GET['responses_requested'])
		cur_page = request.GET['page']
		expanded_question_list = [exp_question]
		exp_answers = expanded_question_list[0].answers.order_by('helpfulCount', '-created_at')[:5]
	except (KeyError, Question.DoesNotExist):
		expanded_question_list = []
		exp_answers = []
		cur_page = utils.get_page_number_from_request(request)
	try:
		res_question = Question.objects.get(pk=request.GET['respond_to_q'])
		cur_page = request.GET['page']
		response_question_list = [res_question]
	except (KeyError, Question.DoesNotExist):
		response_question_list = []
	try: 
		close_q = Question.objects.get(pk=request.GET['close_requested'])
		expanded_question_list= []
		cur_page = request.GET['page']
		exp_answers = []
	except:
		pass

	# questions the user flagged
	try:
		flagged_q = Question.objects.get(pk=request.GET['flag_q'])
		user  = request.user
		flagged_q.inappropriateCount += 1
		flagged_q.inappropriateId.add(user)
		flagged_q.save()
		cur_page = request.GET['page']
		user.flagged_questions.add(flagged_q)
		user.save()
	except:
		pass

	# if user logged in, don't let them reflag question
	try:
		user  = request.user
		flagged_question_list = user.flagged_questions.all()
	except:
		flagged_question_list = []

	
	template = loader.get_template('blog/index.html')
	context = {
		'questions' : questions,
		'expanded_question_list' : expanded_question_list, 
		'response_question_list' : response_question_list, 
		'user': request.user,
		'flagged_question_list': flagged_question_list,
		'expanded_answers': exp_answers,
		'cur_page': cur_page,
	}
	print(cur_page)
	return HttpResponse(template.render(context, request))
	
def blocked(request):
	template = loader.get_template('blog/blocked.html')
	context = {}
	return HttpResponse(template.render(context, request))	


def update_responses(request):
	a = request.POST['response']
	q = request.POST['question_id']
	
	answer = Answer(text=a, user=request.user, created_at=timezone.now(), question=Question.objects.get(pk=q))
	answer.save()
	
	return HttpResponseRedirect(reverse("blog:index"))

def filter(request):
	search_tags = request.GET['tags'].split()
	latest_question_list = Question.objects.order_by('-created_at')
	allowed_question_list = []
	for q in latest_question_list:
		allowed = True
		for t in search_tags:
			if not q.tags.filter(text__iregex = t):
				allowed = False
				break
		
		if allowed:
			allowed_question_list.append(q)
	
	allowed_question_list = allowed_question_list[:5]
	print(search_tags)
	print(allowed_question_list)
	template = loader.get_template('blog/index.html')
	context = {
		'latest_question_list' : allowed_question_list,
		'expanded_question_list' : [], 
		'response_question_list' : [], 
	}
	return HttpResponse(template.render(context, request))

def getq(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'blog/getquestion.html', {'question': question})

def postaq(request):
	if request.method == 'GET':
		return render(request, 'blog/postaq.html', {})
	else:
		q = request.POST['question']
		t = request.POST['tags'].split()
		
		question = Question(text=q, created_at=timezone.now())
		question.save()
		
		for tag in t:
			try:
				t_obj = tag.objects.filter(text = tag)[0]
			except:
				t_obj = Tag(text = tag)
				t_obj.save();
			question.tags.add(t_obj)	
	
		return HttpResponseRedirect(reverse("blog:index"))
	
	
def createprofile(request):
	if request.method == 'POST':
		user = request.user
		netidtxt = user.username
		user.profile.handle = request.POST['handle']
		user.profile.classYear = request.POST['year']
		user.profile.initialized = True
		user.profile.netid = netidtxt
		user.profile.created_at = timezone.now()
		user.profile.save()
		user.save()

		return HttpResponseRedirect(reverse("blog:index"))

	return render(request, 'blog/createprofile.html', {})
    

def loginpage(request):
	context = {
		'user': request.user,
		}
	template = loader.get_template("blog/loginpage.html")
	return HttpResponse(template.render(context, request))

def mod(request):
	if not request.user.is_authenticated or not request.user.profile.modOrNot:
		return HttpResponseRedirect(reverse('blog:index'))
		
	try:
		delete_q = request.POST['delete_q']
		q = Question.objects.get(pk=delete_q)
		q.delete()
	except:
		pass
		
	try:
		hide_r = request.POST['hide_r']
		r = Answer.objects.get(pk=hide_r)
		r.delete()
	except:
		pass
	
	inappropriate_questions = Question.objects.filter(inappropriateCount__gt=0).order_by('inappropriateCount')[:5]
	inappropriate_responses = Answer.objects.filter(inappropriateCount__gt=0).order_by('inappropriateCount')[:5]
	flagged_users = Profile.objects.filter(inappropriateCount__gt=0).order_by('inappropriateCount')[:5]
	
	context = {
		'inappropriate_questions' : inappropriate_questions,
		'inappropriate_responses' : inappropriate_responses,
		'flagged_users' : flagged_users,
	}
	
	template = loader.get_template('blog/mod.html')
	return HttpResponse(template.render(context, request))
