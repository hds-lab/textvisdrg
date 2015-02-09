from rest_framework.views import APIView, Response
from msgvis.api import serializers


class DataTableView(APIView):
    def post(self, request, format=None):
        return Response()


class ExampleMessagesView(APIView):
    def post(self, request, format=None):
        return Response()


class ResearchQuestionsView(APIView):
    def post(self, request, format=None):
        return Response()


class DimensionDistributionView(APIView):
    def post(self, request, format=None):
        return Response()


class FilterSummaryView(APIView):
    def post(self, request, format=None):
        return Response()



