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
	#q_list = Question.objects.order_by('-created_at')
	questions = Question.objects.filter(blockedOrNot=False).order_by('-created_at')
	user = request.user
	#paginator = Paginator(q_list, 5)
	#page = request.GET.get('page')
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
		flagged_q = Question.objects.get(pk=request.POST['flag_q'])
		user  = request.user
		flagged_q.inappropriateCount += 1
		flagged_q.inappropriateId.add(user)
		flagged_q.save()
		user.flagged_questions.add(flagged_q)
		user.save()
		
		cur_page = request.GET['page']
	except:
		pass

	# if user logged in, don't let them reflag question
	try:
		user  = request.user
		flagged_question_list = user.flagged_questions.all()
	except:
		flagged_question_list = []


	#try:
		#questions = paginator.page(page)
	#except PageNotAnInteger:
		#questions = paginator.page(1)
	#except EmptyPage:
		#questions = paginator.page(paginator.num_pages)
	
	template = loader.get_template('blog/index.html')
	context = {
		'questions' : questions,
		'expanded_question_list' : expanded_question_list, 
		'response_question_list' : response_question_list, 
		'user': request.user,
		'flagged_question_list': flagged_question_list,
		'expanded_answers': exp_answers,
		'cur_page': cur_page,
		#'page': page,
		#'page_template': page_template,
	}
	#print(cur_page)
	#if request.is_ajax():
		#template = page_template
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
	
def loginpage(request):
	if request.user.is_authenticated and request.user.profile.blockedOrNot:
		current_time = timezone.now()
		if (current_time - request.user.profile.created_at).days > 7:
			if user.blocked_info.count == 1:
				user.profile.blockedOrNot = False
				user.profile.save()
			
	context = {
		'user': request.user,
		}
	template = loader.get_template("blog/loginpage.html")
	return HttpResponse(template.render(context, request))
	
def blocked(request):
	template = loader.get_template('blog/blocked.html')
	context = {}
	return HttpResponse(template.render(context, request))	
	
def createprofile(request):
	if request.method == 'POST':
		user = request.user
		netidtxt = user.username
		#user.profile = Profile(handle=request.POST['handle'], classYear=request.POST['year'],initialized=True, netid=netidtxt, created_at=timezone.now())
		user.profile.handle = request.POST['handle']
		user.profile.classYear = request.POST['year']
		user.profile.initialized = True
		user.profile.netid = netidtxt
		user.profile.created_at = timezone.now()
		# user.profile.user = user
		# user.profile = profile
		user.profile.save()
		user.save()

		return HttpResponseRedirect(reverse("blog:index"))

	return render(request, 'blog/createprofile.html', {})
    
def inappropriate_qs(request):
	if not request.user.is_authenticated or not request.user.profile.modOrNot:
		return HttpResponseRedirect(reverse('blog:index'))
	try:
		delete_q = request.POST['delete_q']
		q = Question.objects.get(pk=delete_q)
		q.delete()
	except:
		pass
	
	inappropriate_questions = Question.objects.filter(inappropriateCount__gt=0).order_by('-inappropriateCount')
	context = {
		'inappropriate_questions' : inappropriate_questions,
	}
	
	template = loader.get_template('blog/inappropriate_qs.html')
	
	return HttpResponse(template.render(context, request))

def inappropriate_rs(request):
	if not request.user.is_authenticated or not request.user.profile.modOrNot:
		return HttpResponseRedirect(reverse('blog:index'))
	try:
		delete_r = request.POST['delete_r']
		r = Answer.objects.get(pk=delete_r)
		r.blockedOrNot = True
	except:
		pass
	
	inappropriate_responses = Answer.objects.filter(inappropriateCount__gt=0).filter(blockedOrNot=False).order_by('-inappropriateCount')
	context = {
		'inappropriate_responses' : inappropriate_responses,
	}
	
	template = loader.get_template('blog/inappropriate_rs.html')
	
	return HttpResponse(template.render(context, request))
	
def flagged_users(request):
	if not request.user.is_authenticated or not request.user.profile.modOrNot:
		return HttpResponseRedirect(reverse('blog:index'))
	
	try:
		block_user = User.objects.get(pk=request.POST['block_user'])
		block_user.profile.blockedOrNot = True
		block_user.profile.save()
		block_user.save()
		
		try:
			block_user.blocked_info.count += 1
			block_user.blocked_info.blocked_at = timezone.now()
			block_user.blocked_info.save()
		except:
			block_info = Blocked(user=block_user,count=1,blocked_at=timezone.now())
			block_user.blocked_info = block_info
			block_user.blocked_info.save()
			block_user.save()		
	except:
		pass
		
	flagged_profiles = Profile.objects.filter(inappropriateCount__gt=0).filter(blockedOrNot=False).order_by('-inappropriateCount')

	context = {
		'flagged_profiles': flagged_profiles,
	}
	template = loader.get_template('blog/flagged_users.html')
	
	return HttpResponse(template.render(context, request))


def mod(request):
	if not request.user.is_authenticated or not request.user.profile.modOrNot:
		return HttpResponseRedirect(reverse('blog:index'))

	try:
		block_user = User.objects.get(pk=request.POST['block_user'])
		block_user.profile.blockedOrNot = True
		block_user.profile.save()
		
		try:
			block_user.blocked_info.count += 1
			block_user.blocked_info.blocked_at = timezone.now()
			block_user.blocked_info.save()
		except:
			block_info = Blocked(user=block_user,count=1,blocked_at=timezone.now())
			block_user.blocked_info = block_info
			block_user.blocked_info.save()
			block_user.save()		
	except:
		pass
		
	try:
		mod_handle = request.POST['new_mod_handle']
		mod_profile = Profile.objects.filter(handle=mod_handle)[0]
		mod_profile.modOrNot = True
		mod_profile.save()
	except:
		pass
		
	try:
		unblock_handle = request.POST['unblock_user']
		unblock_profile = Profile.objects.filter(handle=unblock_handle)[0]
		unblock_profile.blockedOrNot = False
		unblock_profile.save()
	except:
		pass
	
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
	
	inappropriate_questions = Question.objects.filter(inappropriateCount__gt=0).order_by('-inappropriateCount')[:5]
	inappropriate_responses = Answer.objects.filter(inappropriateCount__gt=0).order_by('-inappropriateCount')[:5]
	flagged_profiles = Profile.objects.filter(inappropriateCount__gt=0).filter(blockedOrNot=False).order_by('-inappropriateCount')[:5]
	
	context = {
		'inappropriate_questions' : inappropriate_questions,
		'inappropriate_responses' : inappropriate_responses,
		'flagged_profiles' : flagged_profiles,
	}
	
	template = loader.get_template('blog/mod.html')
	return HttpResponse(template.render(context, request))