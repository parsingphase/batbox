from django.contrib import admin

# Register your models here.
from .models import AudioRecording


class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'processed', 'recorded_at', 'latitude', 'longitude', 'genus', 'species')


admin.site.register(AudioRecording, AudioRecordingAdmin)
