from urllib import request
from random import randint
from django.contrib.auth import get_user_model, models
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
import re
from datetime import datetime
from incidentmanagementsystem.incidenttracker.models import IncidentData, IncidentSearch
from incidentmanagementsystem.users.api.serializers import UserSerializer

User = get_user_model()


class IncidentDetailSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="reporter_name.username")

    class Meta:
        model = IncidentData
        fields = ["id", "incident_number", "user", "detail", "priority", "status", "reported_date_time", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:incident-detail", "lookup_field": "id"}
        }


class IncidentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentData
        fields = ["incident_number", "reporter_name", "detail", "priority", "reported_date_time",]
        read_only_fields = ("incident_number", "reporter_name", "reported_date_time",)

    def save(self, validated_data):
        detail = validated_data.pop('detail')
        priority = validated_data.pop('priority')

        now = datetime.now()
        year = now.year
        i=0
        while i==0:
            inc_no = randint(10000, 99999)
            incident_number = "RMG" + str(inc_no) + str(year)
            if IncidentData.objects.filter(incident_number=incident_number).exists():
                pass
            else:
                i=1

        instance = IncidentData.objects.create(
            incident_number=incident_number,
            reporter_name=self.context['request'].user,
            detail=detail,
            reported_date_time=now,
            priority=priority,
            # status = ,
        )
        return instance


class IncidentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentData
        fields = ["detail", "priority", "status" ]

    def validate(self, attrs):
        if self.instance.reporter_name != self.context['request'].user:
            raise ValidationError("You are not allowed to update the incident reported by other user.")
        elif self.instance.status == "Closed":
            raise ValidationError("You are not allowed to update the incident with 'Closed' status.")
        return attrs

    def update(self, instance, validated_data):
        instance.detail = validated_data.get('detail', instance.detail)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance



class IncidentSearchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentSearch
        fields = ["search_incident"]

    def save(self, validated_data):
        search_incident = validated_data.pop('search_incident')

        if not IncidentData.objects.filter(incident_number=search_incident,reporter_name=self.context['request'].user).exists():
            raise ValidationError("This incident is not available.")

        IncidentSearch.objects.all().delete()

        instance = IncidentSearch.objects.create(
            search_incident=search_incident,
            user=self.context['request'].user,
        )
        return instance
