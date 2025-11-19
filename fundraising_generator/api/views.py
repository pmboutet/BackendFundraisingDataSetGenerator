from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
import yaml
from .serializers import ConfigurationSerializer, DatasetResponseSerializer
from ..services.generator import FundraisingDataGenerator
from django.http import HttpResponse
import io
import zipfile
import pandas as pd
from datetime import datetime

class GenerateDatasetView(APIView):
    @extend_schema(
        summary='Generate Fundraising Dataset',
        description='''
        Generates a synthetic fundraising dataset based on the provided YAML configuration.
        
        The configuration file should include:
        * Years of data to generate
        * Initial donor database size
        * Channel configurations
        * Campaign themes
        * Demographic settings
        
        The generated data includes:
        * Donor transactions with campaign details
        * Donor profiles with demographic information
        * Campaign performance metrics
        ''',
        request=ConfigurationSerializer,
        responses={
            200: OpenApiExample(
                'File Response',
                value={
                    'content': 'binary file content (ZIP)',
                    'content-type': 'application/zip'
                }
            ),
            400: OpenApiExample(
                'Validation Error',
                value={
                    'error': 'Invalid YAML format',
                    'details': 'Specific error message'
                }
            ),
            401: OpenApiExample(
                'Authentication Error',
                value={
                    'detail': 'Authentication credentials were not provided.'
                }
            )
        },
        methods=['POST'],
        tags=['Dataset Generation']
    )
    def post(self, request):
        """Generate fundraising dataset and return as ZIP file."""
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

            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Convert DataFrames to CSV and add to ZIP
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Import Salesforce mapper
                from ..services.salesforce_mapper import export_to_salesforce_format
                
                # Add transactions CSV (Salesforce NPC format)
                transactions_sf = export_to_salesforce_format(transactions, data_type='transactions')
                transactions_csv = transactions_sf.to_csv(index=False).encode('utf-8')
                zip_file.writestr(f'Gift_Transaction_{timestamp}.csv', transactions_csv)
                
                # Add contacts CSV (Salesforce NPC format)
                contacts_sf = export_to_salesforce_format(contacts, data_type='contacts')
                contacts_csv = contacts_sf.to_csv(index=False).encode('utf-8')
                zip_file.writestr(f'Contact_{timestamp}.csv', contacts_csv)
                
                # Also include original format files for backward compatibility
                transactions_csv_orig = transactions.to_csv(index=False).encode('utf-8')
                zip_file.writestr(f'transactions_{timestamp}.csv', transactions_csv_orig)
                
                contacts_csv_orig = contacts.to_csv(index=False).encode('utf-8')
                zip_file.writestr(f'contacts_{timestamp}.csv', contacts_csv_orig)

            # Prepare the response
            zip_buffer.seek(0)
            response = HttpResponse(
                zip_buffer.getvalue(),
                content_type='application/zip'
            )
            
            # Set filename for download
            response['Content-Disposition'] = f'attachment; filename=fundraising_data_{timestamp}.zip'
            
            return response

        except yaml.YAMLError as e:
            return Response(
                {
                    'error': 'Invalid YAML file format',
                    'details': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )