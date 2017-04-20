from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
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
	
	return HttpResponseRedirect(reverse("blog:index"))

def answer(request, question_id):
    if request.method == 'POST':
	    context = RequestContext(request)
	    answer_text = request.POST['answer']
	    question_id = request.POST['question']
	    q = Question.objects.get(pk=question_id)
    
	    anon_user = User.objects.all()[0]
	    if answer_text.strip() == '':
		    return render(request, 'blog/answer.html', {'message': 'Empty'})
    
	    answer_created = timezone.now()
	    answer = Answer(text = answer_text, user=anon_user, question = q, created_at=answer_created)
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
    return render(request, 'blog/answer.html', {'question': question})


def getq(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'blog/getquestion.html', {'question': question})

def addq(request):
    template = loader.get_template('blog/add.html')
    context = RequestContext(request)

    if request.method == 'POST':
        question_text = request.POST['question']
        tag_text = request.POST['tag']
        user_id = request.POST['user']
        user_obj = User.objects.get(id=user_id)

        if question_text.strip() == '':
            return render(request, 'blog/add.html', {'message': 'Empty'})
        question_created_at = datetime.timezone.now()
        q = Question()
        q.text = question_text
        q.created_at = question_created_at
        q.user = user_obj
        q.save()

        tags = tag_text.split(',')
        for tag in tags:
            try:
                t = Tag.objects.get(id = tag_id)
                q.tags.add(t)
            except Tag.DoesNotExist:
                t = Tag()
                t.text = tag
                t.save()
                q.tags.add(t)

        return HttpResponseRedirect('/')
    return HttpResponse(template.render(context))
