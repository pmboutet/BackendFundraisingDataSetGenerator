from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
import yaml
from .serializers import ConfigurationSerializer, DatasetResponseSerializer
from ..services.generator import FundraisingDataGenerator

YAML_EXAMPLE = '''# Basic Configuration
YEARS: 11
FIRST_YEAR: 2014
INITIAL_DONOR_DATABASE_SIZE: 10000
GLOBAL_CHURN_RATE: 0.99
LOCALISATION: 'en_GB'
GDPR_PROOF: True

# Channel Example: Email
CHANNELS:
  Email:
    distribution: "exponential"
    duration: 5
    initial_nb: 10000
    campaigns:
      prospecting:
        nb: 3
        max_reach_contact: 50000
        transformation_rate: 0.005
        avg_donation: 20
        std_deviation: 15
      retention:
        nb: 12
        transformation_rate: 0.02
        avg_donation: 30
        std_deviation: 10
        cross_sell:
          - ['Email', 100]
          - ['Print', 40]
    target:
      ses_wealth_decile: [1, 8]
    payment:
      Credit/Debit Card: 65
      PayPal: 10
      Mobile Payment App: 10
      Direct Debit: 10
      Cheque: 3
      Bank Transfer: 1
    cost_per_reach: 0.05

# Campaign Themes
CAMPAIGN_THEMES:
  - ["Forest protection", 0.1]
  - ["Carbon emission reduction", 0.15]
  - ["Energy transition", 0.1]

# Target Demographics
WHO_POSSIBILITIES:
  - ["Youth", 0.25]
  - ["Families", 0.2]
  - ["Businesses", 0.15]'''

class GenerateDatasetView(APIView):
    @extend_schema(
        summary='Generate Fundraising Dataset',
        description='''
        Generates a synthetic fundraising dataset based on the provided YAML configuration.
        
        The configuration file should include:
        - Years of data to generate
        - Initial donor database size
        - Channel configurations
        - Campaign themes
        - Demographic settings
        - And other parameters
        
        Example YAML Configuration:
        ```yaml
        {}```
        '''.format(YAML_EXAMPLE),
        request=ConfigurationSerializer,
        responses={200: DatasetResponseSerializer},
        methods=['POST'],
        examples=[
            OpenApiExample(
                'Example Configuration',
                summary='Basic YAML configuration',
                description='Example of a minimal YAML configuration file',
                value={'config_file': YAML_EXAMPLE},
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                'Successful Response',
                value={
                    'transactions': [{
                        'date': '2024-01-15T10:30:00Z',
                        'campaign_start': '2024-01-01T00:00:00Z',
                        'campaign_end': '2024-01-31T00:00:00Z',
                        'channel': 'Email',
                        'campaign_name': '2024-15_Email_Climate_awareness',
                        'campaign_type': 'prospecting',
                        'donation_amount': 50.0,
                        'payment_method': 'Credit Card',
                        'cost': 0.5,
                        'reactivity': 0.02,
                        'contact_id': 'ABC12345',
                        'amount_decile': 5
                    }],
                    'contacts': [{
                        'contact_id': 'ABC12345',
                        'salutation': 'Mr.',
                        'gender': 'male',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'phone': '+1234567890',
                        'address_1': '123 Main St',
                        'address_2': 'Apt 4B',
                        'zip_code': '12345',
                        'city': 'Sample City',
                        'country': 'Sample Country',
                        'job': 'Engineer',
                        'origin_decile': 5,
                        'Creation_date': '2024-01-15T10:30:00Z',
                        'Creation_year': 2024
                    }]
                }
            )
        ]
    )
    def post(self, request):
        """Generate fundraising dataset based on YAML configuration."""
        serializer = ConfigurationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Read and parse YAML configuration
            config_file = serializer.validated_data['config_file']
            config_data = yaml.safe_load(config_file)

            # Generate dataset
            generator = FundraisingDataGenerator(config_data)
            transactions, contacts = generator.generate()

            # Convert DataFrames to JSON-serializable format
            response_data = {
                'transactions': transactions.to_dict('records'),
                'contacts': contacts.to_dict('records')
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except yaml.YAMLError as e:
            return Response(
                {'error': 'Invalid YAML file format', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )