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
	questions = Question.objects.filter(blockedOrNot=False).order_by('-created_at')
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

	# unflag question
	try:
		unflagged_q = Question.objects.get(pk=request.POST['unflag_q'])
		user  = request.user
		unflagged_q.inappropriateCount -= 1
		unflagged_q.inappropriateId.remove(user)
		unflagged_q.save()
		user.flagged_questions.remove(unflagged_q)
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

	
	# mark response as helpful
	try:
		helpful_answer = Answer.objects.get(pk=request.GET['helpful'])
		user = request.user
		helpful_answer.helpfulCount += 1
		helpful_answer.helpfulId.add(user)
		helpful_answer.save()

		user.helpful_responses.add(helpful_answer)
		user.save()

	except: 
		pass

	#no double flagging					    
	try:
		user = request.user
		helpful_responses_list = user.helpful_responses.all()
	except: 
		helpful_responses_list = []

	# un mark response as helpful

	try:
		unhelpful_answer = Answer.objects.get(pk=request.GET['unhelpful'])
		user = request.user
		unhelpful_answer.helpfulCount -= 1
		unhelpful_answer.helpfulId.remove(user)
		unhelpful_answer.save()

		user.helpful_responses.remove(unhelpful_answer)
		user.save()

	except: 
		pass

	#response flagging 
	try:
		inapp_answer = Answer.objects.get(pk=request.GET['inapp'])
		user = request.user
		inapp_answer.inappropriateCount += 1
		inapp_answer.inappropriateId.add(user)
		inapp_answer.save()

		inapp_answer.user.profile.inappropriateCount += 1
		inapp_answer.user.profile.save()
		inapp_answer.user.save()

		user.inappropriate_responses.add(inapp_answer)
		user.save()
	
	except:
		pass

	try:
		user = request.user
		inapp_responses_list = user.inappropriate_responses.all()
	except:
		inapp_responses_list = []

	# unflag as inappropriate

	try:
		un_inapp_answer = Answer.objects.get(pk=request.GET['uninapp'])
		user = request.user
		un_inapp_answer.inappropriateCount -= 1
		un_inapp_answer.inappropriateId.remove(user)
		un_inapp_answer.save()

		un_inapp_answer.user.profile.inappropriateCount -= 1
		un_inapp_answer.user.profile.save()
		un_inapp_answer.user.save()

		user.inappropriate_responses.remove(un_inapp_answer)
		user.save()
	
	except:
		pass
	
	template = loader.get_template('blog/index.html')
	context = {
		'questions' : questions,
		'expanded_question_list' : expanded_question_list, 
		'response_question_list' : response_question_list, 
		'user': request.user,
		'flagged_question_list': flagged_question_list,
		'expanded_answers': exp_answers,
		'cur_page': cur_page,
		'helpful_responses_list': helpful_responses_list, 
		'inapp_responses_list': inapp_responses_list, 
	}

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
	
	template = loader.get_template('blog/index.html')
	context = {
		'questions' : allowed_question_list,
		'expanded_question_list' : [], 
		'response_question_list' : [], 
		'user': request.user,
		'flagged_question_list': [],
		'expanded_answers': [],
		'cur_page': 1,
		'helpful_responses_list': [], 
		'inapp_responses_list': [], 
	}

	return HttpResponse(template.render(context, request))

def getq(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")

	# questions the user flagged
    try:
    	flagged_q = Question.objects.get(pk=request.POST['flag_q'])
    	user  = request.user
    	flagged_q.inappropriateCount += 1
    	flagged_q.inappropriateId.add(user)
    	flagged_q.save()
    	user.flagged_questions.add(flagged_q)
    	user.save()

    except:
    	pass

    # unflag question
    try:
    	unflagged_q = Question.objects.get(pk=request.POST['unflag_q'])
    	user  = request.user
    	unflagged_q.inappropriateCount -= 1
    	unflagged_q.inappropriateId.remove(user)
    	unflagged_q.save()
    	user.flagged_questions.remove(unflagged_q)
    	user.save()

    except:
    	pass
    	
    # if user logged in, don't let them reflag question
    try:
    	user  = request.user
    	flagged_question_list = user.flagged_questions.all()
    except:
    	flagged_question_list = []

    # mark response as helpful
    try:
    	helpful_answer = Answer.objects.get(pk=request.GET['helpful'])
    	user = request.user
    	helpful_answer.helpfulCount += 1
    	helpful_answer.helpfulId.add(user)
    	helpful_answer.save()

    	user.helpful_responses.add(helpful_answer)
    	user.save()

    except: 
    	pass

    #no double flagging
    try:
    	user = request.user
    	helpful_responses_list = user.helpful_responses.all()
    except: 
    	helpful_responses_list = []

    # un mark response as helpful

    try:
    	unhelpful_answer = Answer.objects.get(pk=request.GET['unhelpful'])
    	user = request.user
    	unhelpful_answer.helpfulCount -= 1
    	unhelpful_answer.helpfulId.remove(user)
    	unhelpful_answer.save()

    	user.helpful_responses.remove(unhelpful_answer)
    	user.save()

    except: 
    	pass

    #response flagging 
    try:
    	inapp_answer = Answer.objects.get(pk=request.GET['inapp'])
    	user = request.user
    	inapp_answer.inappropriateCount += 1
    	inapp_answer.inappropriateId.add(user)
    	inapp_answer.save()

    	inapp_answer.user.profile.inappropriateCount += 1
    	inapp_answer.user.profile.save()
	inapp_answer.user.save()

    	user.inappropriate_responses.add(inapp_answer)
    	user.save()

    except:
    	pass

    try:
    	user = request.user
    	inapp_responses_list = user.inappropriate_responses.all()
    except:
    	inapp_responses_list = []

    # unflag as inappropriate

    try:
    	un_inapp_answer = Answer.objects.get(pk=request.GET['uninapp'])
    	user = request.user
    	un_inapp_answer.inappropriateCount -= 1
    	un_inapp_answer.inappropriateId.remove(user)
    	un_inapp_answer.save()

    	un_inapp_answer.user.profile.inappropriateCount -= 1
    	un_inapp_answer.user.profile.save()
	un_inapp_answer.user.save()

    	user.inappropriate_responses.remove(un_inapp_answer)
    	user.save()

    except:
    	pass

    template = loader.get_template('blog/getquestion.html')
    context = {
    	'question': question,
    	'user': request.user,
    	'flagged_question_list': flagged_question_list,
    	'helpful_responses_list': helpful_responses_list, 
    	'inapp_responses_list': inapp_responses_list, 
    	}

    return HttpResponse(template.render(context, request))

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
	handle_in_use = 0
	if request.method == 'POST':
		user = request.user
		netidtxt = user.username
		#user.profile = Profile(handle=request.POST['handle'], classYear=request.POST['year'],initialized=True, netid=netidtxt, created_at=timezone.now())
		handle = request.POST['handle']
		handle_in_use = 0
		for profile_obj in Profile.objects.all():
			if handle == profile_obj.handle:
				handle_in_use = 1
				context = {'handle_in_use': handle_in_use,}
				template = loader.get_template('blog/createprofile.html')
				return HttpResponse(template.render(context, request))

		user.profile.handle = handle 
		user.profile.handle = request.POST['handle']
		user.profile.classYear = request.POST['year']
		user.profile.initialized = True
		user.profile.netid = netidtxt
		user.profile.created_at = timezone.now()
		user.profile.save()
		user.save()

		return HttpResponseRedirect(reverse("blog:index"))

	template = loader.get_template('blog/createprofile.html')
	context = {'handle_in_use': handle_in_use,}
	return HttpResponse(template.render(context, request))

def editprofile(request):
	handle_in_use = 0
	if request.method == 'POST':
		user = request.user
		netidtxt = user.username
		handle = request.POST['handle']
		handle_in_use = 0
		for profile_obj in Profile.objects.all():
			if handle == profile_obj.handle:
				handle_in_use = 1
				context = {'handle_in_use': handle_in_use,}
				template = loader.get_template('blog/editprofile.html')
				return HttpResponse(template.render(context, request))

		user.profile.handle = handle 
		user.profile.handle = request.POST['handle']
		user.profile.classYear = request.POST['year']
		user.profile.initialized = True
		user.profile.netid = netidtxt
		user.profile.created_at = timezone.now()
		user.profile.save()
		user.save()

		return HttpResponseRedirect(reverse("blog:index"))

	template = loader.get_template('blog/editprofile.html')
	context = {'handle_in_use': handle_in_use,}
	return HttpResponse(template.render(context, request))
    
def inappropriate_qs(request):
	if not request.user.is_authenticated or not request.user.profile.modOrNot:
		return HttpResponseRedirect(reverse('blog:index'))
	try:
		delete_q = request.POST['delete_q']
		q = Question.objects.get(pk=delete_q)
		q.blockedOrNot = True
		q.blocked_by = User.objects.get(pk=request.POST['user_id'])
		q.save()
	except:
		pass
	
	inappropriate_questions = Question.objects.filter(inappropriateCount__gt=0).filter(blockedOrNot=False).order_by('-inappropriateCount')
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
		r.blocked_by = User.objects.get(pk=request.POST['user_id'])
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
		if not block_user.profile.modOrNot:
			block_user.profile.blockedOrNot = True
			block_user.profile.blocked_by = User.objects.get(pk=request.POST['user_id'])
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

def see_user_history(request):
	if not request.user.is_authenticated or not request.user.profile.modOrNot:
		return HttpResponseRedirect(reverse('blog:index'))
	
	try:
		det_user = Profile.objects.get(handle=request.GET['det_user']).user
		responses = det_user.answers.all()
	except:
		pass
	
	context = {
		'det_user' : det_user,
		'responses' : responses,
	}
	template = loader.get_template('blog/detailed_user.html')
	
	return HttpResponse(template.render(context, request))

def see_mod_history(request):
	if not request.user.is_authenticated or not request.user.profile.is_admin:
		return HttpResponseRedirect(reverse('blog:index'))
				
	try: # TODO add unblocked by
		unblock_profile = Profile.objects.get(pk=request.POST['unblock_user'])
		unblock_profile.blockedOrNot = False
		unblock_profile.blocked_by = None
		unblock_profile.save()
	except:
		pass
	
	try:
		restore_q = request.POST['restore_q']
		q = Question.objects.get(pk=delete_q)
		q.blockedOrNot = False
		q.blocked_by = None
		q.save()
	except:
		pass
		
	try:
		restore_r = request.POST['restore_r']
		r = Answer.objects.get(pk=hide_r)
		r.blockedOrNot = False
		r.blocked_by = None
		r.save()
	except:
		pass
	
	try:
		mod_prof = Profile.objects.filter(handle=request.GET['mod'])[0]
		mod = mod_prof.user
	except: 
		try:
			mod_prof = Profile.objects.filter(handle=request.POST['mod'])[0]
			mod = mod_prof.user
		except: 
			pass
	
	questions = Question.objects.filter(blocked_by=mod).order_by('-inappropriateCount')[:5]
	responses = Answer.objects.filter(blocked_by=mod).order_by('-inappropriateCount')[:5]
	users = Profile.objects.filter(blocked_by=mod).order_by('-inappropriateCount')[:5]
	
	context = {
		'questions' : questions,
		'responses' : responses,
		'users' : users,
		'mod' : mod,
	}
	
	template = loader.get_template('blog/detailed_mod.html')
	return HttpResponse(template.render(context, request))

def admin(request):
	if not request.user.is_authenticated or not request.user.profile.is_admin:
		return HttpResponseRedirect(reverse('blog:index'))

	try: # should probably put this in Blocked info
		block_user = User.objects.get(pk=request.POST['block_user'])
		block_user.profile.blockedOrNot = True
		block_user.profile.blocked_by = User.objects.get(pk=request.POST['user_id'])
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
		
	try: # TODO add modded by
		mod_handle = request.POST['new_mod_handle']
		mod_profile = Profile.objects.filter(handle=mod_handle)[0]
		mod_profile.modOrNot = True
		mod_profile.save()
	except:
		pass
	
	try: # TODO add admin'd by
		admin_handle = request.POST['new_admin_handle']
		admin_profile = Profile.objects.filter(handle=admin_handle)[0]
		admin_profile.is_admin = True
		admin_profile.save()
	except:
		pass
		
	try: # TODO add unblocked by
		unblock_handle = request.POST['unblock_user']
		unblock_profile = Profile.objects.filter(handle=unblock_handle)[0]
		unblock_profile.blockedOrNot = False
		unblock_profile.save()
	except:
		pass
	
	try:
		delete_q = request.POST['delete_q']
		q = Question.objects.get(pk=delete_q)
		q.blockedOrNot = True
		q.blocked_by = User.objects.get(pk=request.POST['user_id'])
		q.save()
	except:
		pass
		
	try:
		hide_r = request.POST['hide_r']
		r = Answer.objects.get(pk=hide_r)
		r.blockedOrNot = True
		r.blocked_by = User.objects.get(pk=request.POST['user_id'])
		r.save()
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
	
	template = loader.get_template('blog/admin.html')
	return HttpResponse(template.render(context, request))


def mod(request):
	if not request.user.is_authenticated or not request.user.profile.modOrNot:
		return HttpResponseRedirect(reverse('blog:index'))

	try: # should probably put this in Blocked info
		block_user = User.objects.get(pk=request.POST['block_user'])
		if not block_user.profile.modOrNot:
			block_user.profile.blockedOrNot = True
			block_user.profile.blocked_by = User.objects.get(pk=request.POST['user_id'])
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
		
	try: # TODO add modded by
		mod_handle = request.POST['new_mod_handle']
		mod_profile = Profile.objects.filter(handle=mod_handle)[0]
		mod_profile.modOrNot = True
		mod_profile.save()
	except:
		pass
		
	try: # TODO add unblocked by
		unblock_handle = request.POST['unblock_user']
		unblock_profile = Profile.objects.filter(handle=unblock_handle)[0]
		unblock_profile.blockedOrNot = False
		unblock_profile.save()
	except:
		pass
	
	try:
		delete_q = request.POST['delete_q']
		q = Question.objects.get(pk=delete_q)
		q.blockedOrNot = True
		q.blocked_by = User.objects.get(pk=request.POST['user_id'])
		q.save()
	except:
		pass
		
	try:
		hide_r = request.POST['hide_r']
		r = Answer.objects.get(pk=hide_r)
		r.blockedOrNot = True
		r.blocked_by = User.objects.get(pk=request.POST['user_id'])
		r.save()
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
