from django.contrib import admin
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from .models import Poll, Choice,Member
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
import sys
from django.db.models.query import QuerySet
#for password function
import random
import string
#for password function
admin.site.site_header = "JEENISo Administration"
admin.site.site_title = "Jeeniso Admin Area"
admin.site.index_title = "Welcome "

#defing firbase connction

import pyrebase
from getpass import getpass
from firebase import firebase as fire
from firebase.firebase import FirebaseAuthentication
firebaseConfig={
    "apiKey": "AIzaSyD9R3uuH7QBs7Sif4RSPuI24XFJaLzKVrs",
    "authDomain": "vote-administration.firebaseapp.com",
    "databaseURL": "https://vote-administration.firebaseio.com",
    "projectId": "vote-administration",
    "storageBucket": "vote-administration.appspot.com",
    "messagingSenderId": "475155004020",
    "appId": "1:475155004020:web:1dad44fccffeb6a1ba6f21",
    "measurementId": "G-3VEXKMBFDL"
                                                                                                        
}

firebase=pyrebase.initialize_app(firebaseConfig) #configuring the app
database = fire.FirebaseApplication('https://vote-administration.firebaseio.com/', None)
db = firebase.database()
auth =firebase.auth()

def randomString(stringLength=10):
    """Generate a random string of fixed length for password """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class ChoiceInline(admin.TabularInline):
    
    model = Choice
    extra = 3
    fields=("choice_text","votes")
   
   
    def get_max_num(self, request, obj=None, **kwargs):
        max_num = 3
        return max_num

    
    
class PollAdmin(admin.ModelAdmin):
    list_display = (
        'poll_text',
        'status',
        
        'enter_poll',
        

        
    )
    fieldsets = [(None, {'fields': ['poll_text','status']}),
                 ('Date Information', {'fields': ['pub_date'], 'classes': ['collapse']}), ]
    inlines = [ChoiceInline]

           
    def enter_poll(self, obj):

            return format_html('<a class="button" href="/admin/add/poll/%s/change/">View poll</a>' % obj.id)
          

    enter_poll.short_description = 'Enter Poll'
    enter_poll.allow_tags = True
   
    

    
   
    
    #overidng the save method in admin panal
    def save_model(self, request, obj, form, change):
        # custom stuff here
        
        #saving the question in our case obj is question
        
        #saving the question
        obj.save() 
        #get a list of valid choices 
        nbOfVotesFileds=int(request.POST["choice_set-TOTAL_FORMS"])
        listOfVotes=[{"id":request.POST["choice_set-"+str(i)+"-id"],"choice_text":request.POST["choice_set-"+str(i)+"-choice_text"],
       "votes":request.POST["choice_set-"+str(i)+"-votes"]} for i in range(nbOfVotesFileds) ]
        #sending the info li firbase
        print (sys.stderr,nbOfVotesFileds)
        #tawa chmazel only sazving the obj(poll ) and the listOfValidVotes fil firebase that s the easy part
        a=0 
        LatestPoll= database.get("https://vote-administration.firebaseio.com/vote-administration/polls",None)
        if  (LatestPoll is not None ):
            for i in LatestPoll:
                if LatestPoll[i]["poll"]==obj.__str__():
                    database.put('https://vote-administration.firebaseio.com/vote-administration/polls/'+i,'status' ,str(obj.status) )
                    a=1
             
        if a == 0:
            data={
                            "pollID" :obj.id, 
                            "poll":obj.__str__(),
                            "status":str(obj.getStatus()),      
                            }
                        
            result = database.post('/vote-administration/polls',data)
                    
            for i in listOfVotes:
                data1={
                                "poll":obj.__str__(),
                                "choice_text":i["choice_text"],
                                "votes":i["votes"],
                                
                            }
                result1 = database.post('/vote-administration/Choices',data1)
             
        #then just copy and past for the members
    def delete_model(modeladmin, request, queryset):
       
        if(isinstance(queryset,Poll)):
            database = fire.FirebaseApplication('https://vote-administration.firebaseio.com/', None)
            print (sys.stderr,type(queryset))
            pollText=queryset.poll_text
            LatestPoll= database.get("https://vote-administration.firebaseio.com/vote-administration/polls",None)
            for i in LatestPoll:
                if LatestPoll[i]["poll"]==pollText:
                    pollFireBaseId=i
            
            database.delete('https://vote-administration.firebaseio.com/vote-administration/polls/'+pollFireBaseId, None)
            choicesOfThePoll=database.get("https://vote-administration.firebaseio.com/vote-administration/Choices",None)
            for choice in choicesOfThePoll:
                if choicesOfThePoll[choice]["poll"]==pollText:
                    database.delete('https://vote-administration.firebaseio.com/vote-administration/Choices/'+choice, None)

            queryset.delete() 
        else:

            database = fire.FirebaseApplication('https://vote-administration.firebaseio.com/', None)
            print (sys.stderr,type(obj))
            pollText=queryset.poll_text
            LatestPoll= database.get("https://vote-administration.firebaseio.com/vote-administration/polls",None)
            
            for obj in queryset:
                pollText=obj.poll_text
                for i in Latestpoll:
                    if Latestpoll[i]["poll"]==pollText:
                        database.delete('https://vote-administration.firebaseio.com/vote-administration/polls/'+i, None)
                choicesOfThePoll=database.get("https://vote-administration.firebaseio.com/vote-administration/Choices",None)
                for choice in choicesOfThePoll:
                    if choicesOfThePoll[choice]["poll"]==pollText:
                        database.delete('https://vote-administration.firebaseio.com/vote-administration/Choices/'+choice, None)


                obj.delete()  

  
    #overidng the save method in admin panal

class MemberOver(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['name','email','password']}),
                  ]
    def save_model(self, request, obj, form, change):
        if not change:
            obj.setPassword(randomString(10))
            obj.save() 
            auth=firebase.auth()
            email=str(obj.getEmail())
            password=str(obj.getPassword())
            user=auth.create_user_with_email_and_password(email,password)
            #cv
            data={
                "userId":obj.id,
                "userToken":user['idToken'],
                "userName":obj.getName(),
                "userEmail":email,
                "userPassword":password
            }
            result = database.post('/vote-administration/Users',data)

            message_to_send= 'Hello ' + obj.getName()+ '\nThis is your voting app password :\n'+ password +'\nplease log in using the password given and your email'
          
            email_subject = 'Voting app ID'
            message = message_to_send 
            to_email = email ,
            email_from = settings.EMAIL_HOST_USER
            
            
            send_mail( email_subject, message, email_from, to_email )
            
           
        else:
            obj.save()

    def delete_model(modeladmin, request, queryset):
       
        if(isinstance(queryset,Member)):
            database = fire.FirebaseApplication('https://vote-administration.firebaseio.com/', None)
            listOfUsers= database.get("https://vote-administration.firebaseio.com/vote-administration/Users",None)
            for i in listOfUsers:
                if listOfUsers[i]["userEmail"]==queryset.getEmail():
                    database.delete('https://vote-administration.firebaseio.com/vote-administration/Users/'+i, None)
                    
            queryset.delete()

        else:
    
            database = fire.FirebaseApplication('https://vote-administration.firebaseio.com/', None)
            print (sys.stderr,type(obj))
            listOfUsers= database.get("https://vote-administration.firebaseio.com/vote-administration/Users",None)
            for i in listOfUsers:
                if listOfUsers[i]["userEmail"]==queryset.getEmail():
                        database.delete('https://vote-administration.firebaseio.com/vote-administration/polls/'+i, None)
                obj.delete()  
            
          
           

admin.site.register(Poll, PollAdmin)
admin.site.register(Member,MemberOver)


# Register your models here.

