from batbox import settings
# from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from os import listdir


# Create your views here.
def index(request):
    template = loader.get_template('tracemap/index.html')
    audio_files = ['foo']
    session_dir = 'Session 20190430_210036'
    data_dir = settings.BASE_DIR + '/data/' + session_dir
    data_files = listdir(data_dir)

    audio_files = []
    map_files = []

    for file in data_files:
        if file[-4:] == '.wav':
            audio_files.append(session_dir + '/' + file)
        elif file[-4:] == '.kml':
            map_files.append(session_dir + '/' + file)

    # return HttpResponse(repr(data_files))

    context = {'audio': audio_files}
    return HttpResponse(template.render(context, request))
