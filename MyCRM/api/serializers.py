from rest_framework import serializers
from crmApp.models import AliOrdersDetailedInformation
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = AliOrdersDetailedInformation
        fields = ['order', 'gmt_modified', 'gmt_trade_end']