from rest_framework import serializers


class EvaluationRequestSerializer(serializers.Serializer):
    transcript = serializers.CharField(max_length=3000)


class EvaluationResponseSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    feedback = serializers.CharField()

