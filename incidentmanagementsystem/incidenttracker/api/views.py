from attr import attrs
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.exceptions import NotFound
from .serializers import IncidentDetailSerializer, IncidentCreateSerializer, IncidentUpdateSerializer
from .serializers import IncidentSearchCreateSerializer
from incidentmanagementsystem.incidenttracker.models import IncidentData, IncidentSearch

from rest_framework import filters

User = get_user_model()

class IncidentViewSet(RetrieveModelMixin,
                  ListModelMixin,
                  UpdateModelMixin,
                  DestroyModelMixin,
                  CreateModelMixin,
                  GenericViewSet):

    queryset = IncidentData.objects.all()
    lookup_field = "id"

    search_fields = ['incident_number']
    filter_backends = (filters.SearchFilter,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IncidentCreateSerializer

        elif self.request.method == 'PUT':
            return IncidentUpdateSerializer
        else:
            return IncidentDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(serializer.validated_data)
        response_serializer = IncidentDetailSerializer(obj, context={'request': request})
        return Response({"response": response_serializer.data, "status": "success"}, status=status.HTTP_201_CREATED)

    def get_queryset(self, *args, **kwargs):  # used in get_object
        return self.queryset.filter(reporter_name=self.request.user)


    def get_object(self, *args, **kwargs):  # used in update
        self.queryset = self.get_queryset()
        obj = self.queryset.filter(id=self.kwargs['id']).first()
        if not obj:
            raise NotFound("Incident not found.")
        return obj

    def update(self, request, *args, **kwargs):
        data_to_change = {'detail': request.data.get("detail"),
                          'priority': request.data.get("priority"),
                          'status': request.data.get("status"),
                          }
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=data_to_change, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"response": serializer.data, "status": "success"}, status=status.HTTP_202_ACCEPTED)


class IncidentSearchViewSet(RetrieveModelMixin,
                  ListModelMixin,
                  UpdateModelMixin,
                  DestroyModelMixin,
                  CreateModelMixin,
                  GenericViewSet):

    queryset = IncidentData.objects.all()
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IncidentSearchCreateSerializer
        else:
            return IncidentDetailSerializer

    def get_queryset(self, *args, **kwargs):  # used in get_object
        incident_number = IncidentSearch.objects.filter(user=self.request.user).values("search_incident")
        if len(incident_number)==0:
            return self.queryset.filter(reporter_name=self.request.user,incident_number="00")
        else:
            return self.queryset.filter(reporter_name=self.request.user,incident_number=incident_number[0]['search_incident'])


    def get_object(self, *args, **kwargs):  # used in update
        self.queryset = self.get_queryset()
        obj = self.queryset.filter(id=self.kwargs['id']).first()
        if not obj:
            raise NotFound("Incident not found.")
        return obj

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(serializer.validated_data)
        response_serializer = IncidentSearchCreateSerializer(obj, context={'request': request})
        return Response({"response": response_serializer.data, "status": "success"}, status=status.HTTP_201_CREATED)

