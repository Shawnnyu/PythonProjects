from django.db import models

from sqlalchemy import Column, Integer, String, Float
from nbaDjangoCrud.database import Base

class Players(models.Model):

    player_id= models.IntegerField(null=True)
    player_imgurl = models.TextField(null=True)
    player_name= models.TextField(null=True)
    time_frame= models.TextField(null=True)
    points= models.FloatField(null=True)
    ast= models.FloatField(null=True)
    reb=models.FloatField(null=True)
    pie= models.FloatField(null=True)
