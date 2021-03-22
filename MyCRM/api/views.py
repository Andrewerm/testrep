from rest_framework import generics
from crmApp.models import AliOrdersDetailedInformation
from .serializers import SubjectSerializer

class SubjectListView(generics.ListAPIView):
    queryset = AliOrdersDetailedInformation.objects.all()
    serializer_class = SubjectSerializer

class SubjectDetailView(generics.RetrieveAPIView):
    queryset = AliOrdersDetailedInformation.objects.all()
    serializer_class = SubjectSerializer