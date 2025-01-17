from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import yaml
from .serializers import ConfigurationSerializer
from ..services.generator import FundraisingDataGenerator

class GenerateDatasetView(APIView):
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
