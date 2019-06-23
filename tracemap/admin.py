from django.contrib import admin

# Register your models here.
from .models import AudioRecording, Species


class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = (
        'identifier',
        'processed',
        'recorded_at',
        'duration',
        'latitude',
        'longitude',
        'genus',
        'species',
        'recorder_serial',
        'hide'
    )


class SpeciesAdmin(admin.ModelAdmin):
    list_display = (
        'genus',
        'species',
        'common_name',
    )
    search_fields = (
        'genus',
        'species',
        'common_name',
    )


admin.site.register(AudioRecording, AudioRecordingAdmin)
admin.site.register(Species, SpeciesAdmin)
