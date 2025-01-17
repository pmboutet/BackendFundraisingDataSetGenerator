from rest_framework import serializers

class ConfigurationSerializer(serializers.Serializer):
    """Serializer for the fundraising data generation configuration."""
    config_file = serializers.FileField(
        help_text='YAML configuration file containing fundraising generation parameters'
    )

    def validate_config_file(self, value):
        """Validate that the uploaded file is a YAML file."""
        if not value.name.endswith('.yml') and not value.name.endswith('.yaml'):
            raise serializers.ValidationError('File must be a YAML file')
        return value

class TransactionSerializer(serializers.Serializer):
    """Serializer for transaction data output."""
    date = serializers.DateTimeField()
    campaign_start = serializers.DateTimeField()
    campaign_end = serializers.DateTimeField()
    channel = serializers.CharField()
    campaign_name = serializers.CharField()
    campaign_type = serializers.CharField()
    donation_amount = serializers.FloatField()
    payment_method = serializers.CharField()
    cost = serializers.FloatField()
    reactivity = serializers.FloatField()
    contact_id = serializers.CharField()
    amount_decile = serializers.IntegerField()

class ContactSerializer(serializers.Serializer):
    """Serializer for contact data output."""
    contact_id = serializers.CharField()
    salutation = serializers.CharField()
    gender = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    address_1 = serializers.CharField()
    address_2 = serializers.CharField(allow_blank=True)
    zip_code = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    job = serializers.CharField()
    origin_decile = serializers.IntegerField()
    Creation_date = serializers.DateTimeField()
    Creation_year = serializers.IntegerField()

class DatasetResponseSerializer(serializers.Serializer):
    """Serializer for the complete dataset response."""
    transactions = TransactionSerializer(many=True)
    contacts = ContactSerializer(many=True)