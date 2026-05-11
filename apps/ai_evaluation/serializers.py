from rest_framework import serializers


class EvaluationRequestSerializer(serializers.Serializer):
    transcript = serializers.CharField(max_length=3000)
    student_id = serializers.IntegerField()
    session_id = serializers.IntegerField()
    evaluation_type = serializers.ChoiceField(choices=[
        ('memorization', 'Memorization'),
        ('recitation', 'Recitation'),
    ])


class EvaluationResponseSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    feedback = serializers.CharField()

