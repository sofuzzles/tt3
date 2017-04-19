# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
 
from . import managers

# User model
class User(models.Model):
    # Relations
    # Attributes - Mandatory
    username = models.CharField(max_length = 50)
    created_at = models.DateTimeField()
    netid = models.CharField(max_length = 50)
    modOrNot = models.BooleanField(default = False)
    blockedOrNot = models.BooleanField(default = False)
    classYear = models.CharField(max_length = 10)
    # Attributes - Optional
    # Object Manager
    objects = managers.UserManager()
    # Custom Properties
    # Methods
    # Meta and String
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
    	return self.username

# Question model
class Question(models.Model):
    # Relations
    user = models.ForeignKey(User, related_name='questions')
    # Attributes - Mandatory
    text = models.TextField()
    created_at = models.DateTimeField()
    blockedOrNot = models.BooleanField(default = False)
    inappropriateCount = models.IntegerField(
        default=0,
        verbose_name= "Inappropriate")
    # Attributes - Optional
    inappropriateId = models.ManyToManyField(User, related_name = '+')
    # Object Manager
    objects = managers.QuestionManager()
    # Custom Properties
    @property
    def username(self):
        return self.user.username
    # Methods
    # Meta and String
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ("user",)
        
    def __str__(self):
        return self.text


# Answer model
class Answer(models.Model):
    # Relations
    user = models.ForeignKey(User, related_name='answers')
    question = models.ForeignKey(Question, related_name='answers')
    # Attributes - Mandatory
    text = models.TextField()
    created_at = models.DateTimeField()
    blockedOrNot = models.BooleanField(default = False)
    inappropriateCount = models.IntegerField(
        default=0,
        verbose_name= "Inappropriate")
    helpfulCount = models.IntegerField(
        default=0,
        verbose_name = "Helpful")
    # Attributes - Optional
    inappropriateId = models.ManyToManyField(User, related_name = '+')
    helpfulId = models.ManyToManyField(User, related_name = '+')
    # Object Manager
    objects = managers.AnswerManager()
    # Custom Properties
    @property
    def username(self):
        return self.user.username
    def qid(self):
        return self.question.id
    # Methods
    # Meta and String
    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ("question","user",)
        
    def __str__(self):
        return self.text

# Tag model
class Tag(models.Model):
    # Relations
    questions = models.ManyToManyField(Question, related_name = 'tags') # might want to change this for symmetry
    
    # Attributes - Mandatory
    text = models.CharField(max_length = 30)

    # Attributes - Optional
    # Object Manager
    objects = managers.TagManager()
    # Custom Properties      
    @property
    def get_questions(self):
    	return self.questions  
    # Methods	
    # Meta and String
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ("text",)
        
    def __str__(self):
        return self.text