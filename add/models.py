from django.db import models
from django.utils.timezone import now



class Poll(models.Model):
    poll_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published',default=now)
    status_choices = (
        ('open', 'open'),
        ('closed', 'closed'),
       
    ) 
    status = models.CharField(max_length=15, choices=status_choices, default=status_choices[0][0])
  
    def getStatus(self):
        return (self.status)
    
    def oppositStatus(self):
        if (self.status=='open'):
            self.status='closed'
        else:
            self.status='open'
        return (self.status)
        
    
    def __str__(self):
        return self.poll_text
    def getPollInfo(self):
        info={"poll_text":self.poll_text,"date":self.pub_date,"status":self.status}
        return(info)
    


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)
    choice_choices = (
        ('yes', 'yes'),
        ('no', 'no'),
        ('refrain', 'refrain'),
    )
    choice_text = models.CharField(max_length=15, choices=choice_choices, default=choice_choices[0][0])
 

    def __str__(self):
        return self.choice_text
        
    def getChoiseInfo(self):
        return({"Poll":self.poll,"choice":self.choice_text,"votes":self.votes})

class Member (models.Model):
    #name , email ,password
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100,blank=True)

    def __str__(self):
        return(self.name)
    
    def getName(self):
        return(self.name)
    def getPassword(self):
        return(self.password)
    def getEmail(self):
        return(self.email)
    def setPassword(self,newPass):
        self.password=newPass
    def setMail(self,newEmail):
        self.email=newEmail


class sortingpolls (models.Model):
    poll = models.CharField(max_length=200)
    pollID = models.CharField(max_length=200)

    def __init__(self,poll,pollID,status):
        self.poll=poll
        self.pollID=pollID
        self.status=status

    def __str__(self):
        return(self.poll)
   
    
# Create your models here.

