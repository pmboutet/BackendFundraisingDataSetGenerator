from django.urls import path
from .api.views import GenerateDatasetView

urlpatterns = [
    path('generate/', GenerateDatasetView.as_view(), name='generate-dataset'),
]
