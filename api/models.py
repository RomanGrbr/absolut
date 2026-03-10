from django.conf import settings
from django.db import models


class Survey(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Описание', blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='authored_surveys',
        verbose_name='Автор',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата изменения', auto_now=True)

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'опросы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Опрос',
    )
    text = models.TextField('Текст вопроса')
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'вопросы'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.survey.title} - Вопрос {self.order}: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Вопрос',
    )
    text = models.CharField('Текст варианта', max_length=255)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'варианты ответов'
        ordering = ['order']

    def __str__(self):
        return f'{self.question} → {self.text[:50]}'


class SurveySession(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='Опрос',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='survey_sessions',
        verbose_name='Пользователь',
    )
    started_at = models.DateTimeField('Начато', auto_now_add=True)
    completed_at = models.DateTimeField('Завершено', null=True, blank=True)

    class Meta:
        verbose_name = 'Прохождение опроса'
        verbose_name_plural = 'прохождения опросов'
        constraints = [
            models.UniqueConstraint(
                fields=('survey', 'user'),
                name='unique_survey_user',
            ),
        ]

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    @property
    def duration_seconds(self) -> float | None:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def __str__(self):
        status = 'завершён' if self.is_completed else 'в процессе'
        return f'{self.user} → {self.survey} ({status})'


class Answer(models.Model):
    session = models.ForeignKey(
        SurveySession,
        on_delete=models.CASCADE,
        verbose_name='Сеанс',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='Вопрос',
    )
    choices = models.ManyToManyField(
        Choice,
        verbose_name='Выбранные варианты',
        blank=True,
    )
    answered_at = models.DateTimeField('Время ответа', auto_now_add=True)

    class Meta:
        default_related_name = 'answers'
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'ответы пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=('session', 'question'),
                name='unique_session_question',
            ),
        ]

    def __str__(self):
        return f'Сеанс {self.session_id} / Вопрос {self.question}'
