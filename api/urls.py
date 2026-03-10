from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import (AnswerViewSet, NextQuestionView, QuestionViewSet, SurveySessionViewSet, SurveyStatView,
                    SurveyViewSet,)

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename='survey')
router.register(r'sessions', SurveySessionViewSet, basename='session')
router.register(r'answers', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'surveys/<int:survey_pk>/questions/',
        QuestionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='survey-question-list',
    ),
    path(
        'surveys/<int:survey_pk>/questions/<int:pk>/',
        QuestionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='survey-question-detail',
    ),
    path(
        'surveys/<int:survey_pk>/next-question/',
        NextQuestionView.as_view(),
        name='survey-next-question',
    ),
    path(
        'surveys/<int:survey_pk>/stats/',
        SurveyStatView.as_view(),
        name='survey-stats',
    ),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
