from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.static import players
import re
import io
from zipfile import ZipFile
from django.urls import path
from .models import*
import pandas as pd
import configparser
import boto3 as boto3
###
from bs4 import BeautifulSoup
import requests

config = configparser.ConfigParser()
config.read('player_register/app.config')

aws_access_key=config.get('AWS','AWS_ACCESS_KEY')
aws_secret_access_key=config.get('AWS','AWS_SECRET_ACCESS_KEY')
service_name=config.get('AWS','SERVICE_NAME')
region_name=config.get('AWS','REGION_NAME')
bucket_name=config.get('AWS','BUCKET_NAME')

filepath=config.get('PATH','filepath')
filekey=config.get('PATH','key')

default_img=config.get('PLAYER_DB','default_img')

s3= boto3.resource(
     service_name = service_name,
     region_name=region_name,
     aws_access_key_id=aws_access_key,
     aws_secret_access_key=aws_secret_access_key
 )

def getPlayerInfo(player_name: str):
    player_id=players.find_players_by_full_name(re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', player_name))[0]['id']
    player_info = commonplayerinfo.CommonPlayerInfo(player_id)
    player_dict = player_info.player_headline_stats.get_dict()
    return player_dict

###
def getPlayerImgUrl(player_id):
    url = f'https://www.nba.com/player/{player_id}/'
    r = requests.get(url)
    soup=BeautifulSoup(r.text, 'html.parser')
    images=soup.find('img', {"class":'PlayerImage_image__wH_YX PlayerSummary_playerImage__sysif'})
    img_link = images.get("src")
    return img_link


def index(request):
    item_list = Players.objects.all()
    context = {
        'item_list' : item_list
    }

    return render(request, 'index.html', context)


def add_item(request):
    if request.method=="POST":
        name=request.POST['name']
        if not name:
            messages.info(request, f"Player {name} not found")
            return redirect("index")
        else:
            player_model = Players()
            try:
                player_info = getPlayerInfo(name)
            except:
                messages.info(request, f"Player {name} not found")
                return redirect("index")
            ###
            player_id=player_info.get('data')[0][0]
            player_model.player_id=player_id
            player_model.player_imgurl=getPlayerImgUrl(player_id)
            ###
            player_model.player_name=player_info.get('data')[0][1]
            player_model.time_frame=player_info.get('data')[0][2]
            player_model.points=player_info.get('data')[0][3]
            player_model.ast=player_info.get('data')[0][4]
            player_model.reb=player_info.get('data')[0][5]
            player_model.pie=player_info.get('data')[0][6]
            player_model.save()
            messages.info(request, f"player added successfully {name}")
            #description=request.POST['description']
    else:
        pass

    return redirect("index")


def create_item(request):
    player = Players()
    
    #player.player_id = sys.maxsize
    player.player_id = None
    ###
    player.player_imgurl = default_img
    ###
    player.player_name = request.POST['name']  or None
    player.time_frame = request.POST['timeFrame']  or None
    player.points = request.POST['points'] or None
    player.ast = request.POST['assists']  or None
    player.reb = request.POST['rebounds']  or None
    player.pie = request.POST['pie']  or None
    player.save()
    messages.info(request,"Player created successfully")
    return redirect("index")


def delete_item(request,myid):
    player=Players.objects.get(id=myid)
    player.delete()
    messages.info(request,"Player deleted successfully")
    return redirect("index")


def edit_item(request,myid):
     sel_item = Players.objects.get(id=myid)
     item_list = Players.objects.all()
     context = {
         'sel_item': sel_item,
        'item_list' : item_list
     }
     return render(request, 'index.html', context)


def update_item(request, myid):
    player = Players.objects.get(id = myid)
    player.player_name = request.POST['name']
    player.time_frame = request.POST['timeFrame']
    player.points = request.POST['points']
    player.ast = request.POST['assists']
    player.reb = request.POST['rebounds']
    player.pie = request.POST['pie']
    player.save()
    messages.info(request,"Player updated successfully")
    return redirect("index")

def upload_s3_and_csv(request):
    if request.method == "GET":
        df= pd.DataFrame(Players.objects.all().values())
        df.to_csv('/playerDB.csv')
        s3.Bucket(bucket_name).upload_file(Filename=filepath, Key=filekey)
    else:
        pass

    return redirect("index")

def upload_s3(request):
    if request.method == "GET":
        df= pd.DataFrame(Players.objects.all().values())
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer)
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'a') as zf:
            zf.writestr('playerDB.csv', csv_buffer.getvalue())
        
        s3_resource = boto3.resource('s3')
        s3_resource.Object(bucket_name, 'playerDB.csv').put(Body=zip_buffer.getvalue())
        messages.info(request,"Uploaded to s3 successfully")
    else:
        pass

    return redirect("index")