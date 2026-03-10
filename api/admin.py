from django.contrib import admin

from .models import Survey, Question, Choice, SurveySession, Answer


@admin.register(Survey, Question, Choice, SurveySession, Answer)
class AllAdmin(admin.ModelAdmin):...
