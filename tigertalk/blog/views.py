from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Question, Tag, Profile, Answer

def index(request):
	latest_question_list = Question.objects.order_by('-created_at')[:5]
	try:
		exp_question = Question.objects.get(pk=request.GET['responses_requested'])
		expanded_question_list = [exp_question]
	except (KeyError, Question.DoesNotExist):
		expanded_question_list = []
	
	try:
		res_question = Question.objects.get(pk=request.GET['respond_to_q'])
		response_question_list = [res_question]
	except (KeyError, Question.DoesNotExist):
		response_question_list = []
	
	try:
		close_q = Question.objects.get(pk = request.GET['close_requested'])
		expanded_question_list = []
	except:
		pass
	
	template = loader.get_template('blog/index.html')
	context = {
		'latest_question_list' : latest_question_list,
		'expanded_question_list' : expanded_question_list, 
		'response_question_list' : response_question_list, 
		'user': request.user,
	}
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
		
def answer(request, question_id):
    if request.user.is_anonymous():
	    return HttpResponseRedirect("/accounts/login/")
    if request.method == 'POST':
	    context = RequestContext(request)
	    answer_text = request.POST['answer']
	    question_id = request.POST['question']
	    q = Question.objects.get(pk=question_id)
    
	    user_id = request.POST['user']
	    user = User.objects.get(id=user_id)
	    prof = Profile.objects.get(user=user)
	    prof.save()
	    if answer_text.strip() == '':
		    return render(request, 'blog/answer.html', {'message': 'Empty'})
    
	    answer_created = timezone.now()
	    answer = Answer(text = answer_text, profile=prof, question = q, created_at=answer_created)
	    answer.save()
	    answer_list = question.answer_set.order_by('-created_at')
	    paginator = Paginator(answer_list, 10)
	    page = request.GET.get('page')
	    try:
		    answers = paginator.page(page)
	    except PageNotAnInteger:
		    # If page is not an integer, deliver first page.
		    answers = paginator.page(1)
	    except EmptyPage:
		    # If page is out of range (e.g. 9999), deliver last page of results.
		    answers = paginator.page(paginator.num_pages)
	    return render(request, 'blog/answer.html', {'question': question, 'answers': answers})
    return render(request, 'blog/answer.html', {'question': Question.objects.get(pk=question_id)})


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
