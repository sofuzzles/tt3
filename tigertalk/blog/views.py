from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Question, Tag, Profile, Answer

def index(request):
	q_list = Question.objects.order_by('-created_at')
	user = request.user
	paginator = Paginator(q_list, 5)
	page = request.GET.get('page')
	try:
		exp_question = Question.objects.get(pk=request.GET['responses_requested'])
		expanded_question_list = [exp_question]
		exp_answers = expanded_question_list[0].answers.order_by('helpfulCount', '-created_at')[:5]
	except (KeyError, Question.DoesNotExist):
		expanded_question_list = []
		exp_answers = []
	try:
		res_question = Question.objects.get(pk=request.GET['respond_to_q'])
		response_question_list = [res_question]
	except (KeyError, Question.DoesNotExist):
		response_question_list = []
	try: 
		close_q = Question.objects.get(pk=request.GET['close_requested'])
		expanded_question_list= []
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


	try:
		questions = paginator.page(page)
	except PageNotAnInteger:
		questions = paginator.page(1)
	except EmptyPage:
		questions = paginator.page(paginator.num_pages)
	
	template = loader.get_template('blog/index.html')
	context = {
		'questions' : questions,
		'expanded_question_list' : expanded_question_list, 
		'response_question_list' : response_question_list, 
		'user': request.user,
		'flagged_question_list': flagged_question_list,
		'expanded_answers': exp_answers,
	}
	return HttpResponse(template.render(context, request))
	
def blocked(request):
	template = loader.get_template('blog/blocked.html')
	context = {}
	return HttpResponse(template.render(context, request))	


def update_responses(request):
#	if request.user.is_anonymous():
#		return HttpResponseRedirect("/accounts/login/")
	a = request.POST['response']
	q = request.POST['question_id']
	
	#user_id = request.POST['user_id']
	#userobj = User.objects.get(id=user_id)
	#netidtxt = request.user.username
      		
	# prof.save()
	#anon_user = User.objects.all()[0]
	
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
		
		anon_user = User.objects.all()[0]
		question = Question(text=q, user=anon_user, created_at=timezone.now())
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
		profile = Profile(handle=request.POST['handle'], classYear=request.POST['year'], user=user,initialized=True, netid=netidtxt, created_at=timezone.now())
		profile.save()
		#profile.handle = request.POST['handle']
		#profile.classYear = request.POST['year']
		#profile.initiated = True
		#profile.netid = netidtxt
		#profile.created_at = timezone.now()
		#profile.user = user
		#profile.save()
		user.profile = profile
		user.profile.save()
		user.save()
		#user.profile.handle = request.POST['handle']
		#user.profile.classYear  = request.POST['year']
		#user.profile.initiated = True
		#user.profile.netid = netidtxt
		#user.profile.created_at = timezone.now()
		#user.profile.save()
		#user.save()

		return HttpResponseRedirect(reverse("blog:index"))

	return render(request, 'blog/createprofile.html', {})
    

def loginpage(request):
	context = {
		'user': request.user,
		}
	template = loader.get_template("blog/loginpage.html")
	return HttpResponse(template.render(context, request))
