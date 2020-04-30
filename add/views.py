from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.http import JsonResponse

from .models import Poll, Choice, sortingpolls

from firebase import firebase as fire

class fireStuff :
  def __init__(self,poll,pollID):
    self.poll=poll
# Get questions and display them
def index(request):
    latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
    #question from firebase
    firebase = fire.FirebaseApplication('https://vote-administration.firebaseio.com/', None)
    LatestPoll= firebase.get("https://vote-administration.firebaseio.com/vote-administration/polls",None)

    if(LatestPoll):
      indexs=[i for i in LatestPoll]
      jasonpk=[LatestPoll[i] for i in indexs]
    else:
      indexs=[]
      jasonpk=[]
    #question from firebase
    context = {'latest_poll_list': latest_poll_list ,"LatestPoll":LatestPoll,"jasonpk":jasonpk}
    return render(request, 'polls/index.html', context)

# Show specific question and choices
def detail(request, poll_id):
  try:
    poll = Poll.objects.get(pk=poll_id)
   
  except Poll.DoesNotExist:
    raise Http404("Poll does not exist")
  return render(request, 'polls/detail.html', { 'poll': poll })

# Get question and display results
def results(request, poll_id):
  #question from firebase
  firebase = fire.FirebaseApplication('https://vote-administration.firebaseio.com/', None)
  LatestPoll= firebase.get("https://vote-administration.firebaseio.com/vote-administration/polls",None)
  indexs=[i for i in LatestPoll]
  jasonpk=[LatestPoll[i] for i in indexs]
  pollFire=[i for i in jasonpk if i["pollID"]==poll_id][0]
  #question from firebase

  #choice from firebase
 
  LatestChoices= firebase.get("https://vote-administration.firebaseio.com/vote-administration/Choices",None)
  indexs=[i for i in LatestChoices]
  jasonpk2=[LatestChoices[i] for i in indexs]
  choisesFire=[i for i in jasonpk2 if i["poll"]==pollFire["poll"]]
  #choice from firebase
  poll = get_object_or_404(Poll, pk=poll_id)

  return render(request, 'polls/results.html', { "pollFire":pollFire ,"choisesFire":choisesFire})

# Vote for a question choice
def vote(request, poll_id):
    # print(request.POST['choice'])
    poll = get_object_or_404(poll, pk=poll_id)
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'poll': poll,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(poll.id,)))

def resultsData(request, obj):
    votedata = []

    poll = Poll.objects.get(id=obj)
    votes = poll.choice_set.all()

    for i in votes:
        votedata.append({i.choice_text:i.votes})

    print(votedata)
    return JsonResponse(votedata, safe=False)


# Create your views here.
