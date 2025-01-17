from rest_framework import serializers

class ConfigurationSerializer(serializers.Serializer):
    config_file = serializers.FileField()

    def validate_config_file(self, value):
        """Validate that the uploaded file is a YAML file."""
        if not value.name.endswith('.yml') and not value.name.endswith('.yaml'):
            raise serializers.ValidationError('File must be a YAML file')
        return value
