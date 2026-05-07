from rest_framework import serializers


class AssistantPromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000)


class AssistantResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    provider = serializers.CharField(default="stub")

