# -*- coding: utf-8 -*-
from django.db import models
 
 
class ProfileManager(models.Manager):
    pass

class QuestionManager(models.Manager):
    pass

class AnswerManager(models.Manager):
    pass
    
class TagManager(models.Manager):
	pass

class BlockedManager(models.Manager):
	pass

class GenericManager(models.Manager):
	pass
