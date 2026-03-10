from django.db.models import Avg, Count, DurationField, F, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.response import Response

from .models import Answer, Question, Survey, SurveySession
from .permissions import IsAdminOrReadOnly, IsAdminUser
from .serializers import (AnswerSerializer, QuestionSerializer,
                          QuestionWriteSerializer, SurveyDetailSerializer,
                          SurveyListSerializer, SurveySessionSerializer,
                          SurveyStatSerializer, SurveyWriteSerializer)


class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Survey.objects.select_related('author')
        if self.action == 'list':
            qs = qs.annotate(questions_count=Count('questions'))
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return SurveyListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return SurveyWriteSerializer
        return SurveyDetailSerializer


    def retrieve(self, request, *args, **kwargs):
        instance = (
            Survey.objects
            .prefetch_related('questions__choices')
            .get(pk=kwargs['pk'])
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Question.objects.none()
        return (
            Question.objects
            .filter(survey_id=self.kwargs['survey_pk'])
            .prefetch_related('choices')
        )

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return QuestionSerializer
        return QuestionWriteSerializer

    def perform_create(self, serializer):
        serializer.save(survey=get_object_or_404(Survey, pk=self.kwargs['survey_pk']))


class SurveySessionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SurveySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SurveySession.objects.none()
        return (
            SurveySession.objects
            .filter(user=self.request.user)
            .select_related('survey')
        )


class AnswerViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['session']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Answer.objects.none()
        return (
            Answer.objects
            .filter(session__user=self.request.user)
            .select_related('question', 'choice')
        )

    def perform_create(self, serializer):
        answer = serializer.save()
        session = answer.session
        if session.answers.count() == session.survey.questions.count():
            session.completed_at = timezone.now()
            session.save(update_fields=['completed_at'])


class NextQuestionView(generics.GenericAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Следующий вопрос опроса',
        description=(
            'Возвращает следующий неотвеченный вопрос для текущего пользователя.'
        ),
        responses={
            status.HTTP_200_OK: QuestionSerializer,
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        survey_pk = self.kwargs['survey_pk']
        session = (
            SurveySession.objects
            .filter(survey_id=survey_pk, user=request.user, completed_at__isnull=True)
            .first()
        )
        if session is None:
            return Response(
                {'detail': 'Активный сеанс не найден.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        answered_question_ids = set(
            session.answers
            .values_list('question_id', flat=True)
        )
        next_question = (
            Question.objects
            .filter(survey_id=survey_pk)
            .exclude(id__in=answered_question_ids)
            .prefetch_related('choices')
            .first()
        )
        if next_question is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(next_question)
        return Response(serializer.data)


class SurveyStatView(generics.GenericAPIView):
    serializer_class = SurveyStatSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, pk=kwargs['survey_pk'])

        sessions_agg = survey.sessions.aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(completed_at__isnull=False)),
            avg_sec=Avg(
                F('completed_at') - F('started_at'),
                output_field=DurationField(),
                filter=Q(completed_at__isnull=False),
            ),
        )
        avg_duration = sessions_agg['avg_sec'].total_seconds() if sessions_agg['avg_sec'] else None

        questions = (
            survey.questions
            .prefetch_related(
                Prefetch(
                    'answers',
                    queryset=Answer.objects
                        .filter(session__survey=survey)
                        .select_related('session__user', 'choice'),
                )
            )
        )

        questions_stat = []
        for q in questions:
            questions_stat.append({
                'question_id': q.pk,
                'question_text': q.text,
                'answers': [
                    {
                        'username': a.session.user.username,
                        'choice_id': a.choice_id,
                        'choice_text': a.choice.text,
                    }
                    for a in q.answers.all()
                ],
            })

        data = {
            'survey_id': survey.pk,
            'total_sessions': sessions_agg['total'],
            'completed_sessions': sessions_agg['completed'],
            'avg_duration_seconds': avg_duration,
            'questions': questions_stat,
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)
