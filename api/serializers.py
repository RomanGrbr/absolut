from rest_framework import serializers

from .models import Answer, Choice, Question, Survey, SurveySession


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'text', 'order')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'choices')


class QuestionWriteSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'choices')

    def _save_choices(self, question: Question, choices_data: list) -> None:
        existing_ids = {c['id'] for c in choices_data if c.get('id')}
        question.choices.exclude(id__in=existing_ids).delete()

        for data in choices_data:
            choice_id = data.pop('id', None)
            if choice_id:
                Choice.objects.update_or_create(
                    id=choice_id,
                    defaults={**data, 'question': question},
                )
            else:
                Choice.objects.create(**data, question=question)

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        self._save_choices(question, choices_data)
        return question

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', None)
        if choices_data is not None:
            self._save_choices(instance, choices_data)
        return super().update(instance, validated_data)


class SurveyBaseSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'author_username', 'created_at')


class SurveyListSerializer(SurveyBaseSerializer):
    questions_count = serializers.IntegerField(read_only=True)

    class Meta(SurveyBaseSerializer.Meta):
        fields = SurveyBaseSerializer.Meta.fields + ('questions_count',)


class SurveyDetailSerializer(SurveyBaseSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta(SurveyBaseSerializer.Meta):
        fields = SurveyBaseSerializer.Meta.fields + ('questions',)


class SurveyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('id', 'title')

    def create(self, validated_data: dict) -> Survey:
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class SurveySessionSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.FloatField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = SurveySession
        fields = ('id', 'survey', 'started_at', 'completed_at', 'is_completed', 'duration_seconds')
        read_only_fields = ('id', 'started_at', 'completed_at', 'is_completed', 'duration_seconds')

    def validate_survey(self, survey: Survey) -> Survey:
        user = self.context['request'].user
        if user.survey_sessions.filter(survey=survey).exists():
            raise serializers.ValidationError('Вы уже проходили этот опрос.')
        return survey

    def create(self, validated_data: dict) -> SurveySession:
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    choice = serializers.PrimaryKeyRelatedField(
        queryset=Choice.objects.all(),
    )

    class Meta:
        model = Answer
        fields = ('id', 'session', 'question', 'choice', 'answered_at')
        read_only_fields = ('id', 'answered_at')

    def validate(self, attrs: dict) -> dict:
        session  = attrs['session']
        question = attrs['question']

        if question.survey_id != session.survey_id:
            raise serializers.ValidationError(
                'Вопрос не принадлежит опросу данного сеанса.'
            )

        request = self.context['request']
        if session.user_id != request.user.pk:
            raise serializers.ValidationError('Это не ваш сеанс.')

        if attrs['choice'].question_id != question.pk:
            raise serializers.ValidationError(
                f'Вариант {attrs["choice"].pk} не принадлежит вопросу {question.pk}.'
            )

        if session.answers.filter(question=question).exists():
            raise serializers.ValidationError('Вы уже ответили на этот вопрос.')

        return attrs


class ChoiceStatSerializer(serializers.Serializer):
    choice_id = serializers.IntegerField()
    choice_text = serializers.CharField()
    count = serializers.IntegerField()


class QuestionStatSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question_text = serializers.CharField()
    answers_count = serializers.IntegerField()
    choices = ChoiceStatSerializer(many=True)


class SurveyStatSerializer(serializers.Serializer):
    survey_id = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    completed_sessions = serializers.IntegerField()
    avg_duration_seconds = serializers.FloatField(allow_null=True)
    questions = QuestionStatSerializer(many=True)
