from django.contrib.auth.models import User
from django.db import models


class Survey(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='authored_surveys', verbose_name= 'Автор')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'опросы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions', verbose_name = 'Опрос')
    text = models.TextField('Текст')
    order = models.PositiveIntegerField('Очередность', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'вопросы'
        ordering = ['order']
        constraints = (
            models.UniqueConstraint(
                fields=('survey', 'order'),
                name='unique_survey_order',
            ),
        )

    def __str__(self):
        return f"{self.survey.title} - Вопрос {self.order}: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name = 'Вопрос')
    text = models.CharField('Текст', max_length=255)
    order = models.PositiveIntegerField('Очередность', default=0)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'ответы'
        ordering = ['order']
        constraints = (
            models.UniqueConstraint(
                fields=('question', 'order'),
                name='unique_question_order',
            ),
        )

    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"


class SurveySession(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Прохождение опроса'
        verbose_name_plural = 'прохождение опросов'
        constraints = (
            models.UniqueConstraint(
                fields=('survey', 'user'),
                name='unique_survey_user',
            ),
        )

    @property
    def duration_seconds(self):
        """Время прохождения в секундах"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def __str__(self):
        return f"{self.user.username} - {self.survey.title}"


class Answer(models.Model):
    session = models.ForeignKey(SurveySession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = 'answers'
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'ответы пользователей'
        constraints = (
            models.UniqueConstraint(
                fields=('session', 'question'),
                name='unique_session_question',
            ),
        )

    def __str__(self):
        return f"Ответ {self.session.user} на {self.question}"
