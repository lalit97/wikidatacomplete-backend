import json
from random import choice
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Fact
from backend.serializers import FactListCreateSerializer


class FactListCreateAPI(generics.ListCreateAPIView):
    queryset = Fact.objects.all()
    serializer_class = FactListCreateSerializer


class FactRetrieveUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fact.objects.all()
    serializer_class = FactListCreateSerializer


class RetrieveFactWithQIdAPI(APIView):
    def get(self, request, *args, **kwargs):
        qid = self.kwargs.get("qid")
        try:
            custom_response = []
            facts_qs = Fact.objects.filter(wikidata_entity__endswith=qid)
            for fact in facts_qs:
                evidence_highlight = fact.evidence_highlight
                meta_information = fact.meta_information
                references = fact.references
                evidence, wikipedia_link = None, None  # setting default values
                for refer in references:
                    if refer.get("type") == "string":
                        evidence = refer.get("value")
                    elif refer.get("type") == "url":
                        wikipedia_link = refer.get("value")
                custom_response.append(
                    {
                        "id": fact.id,
                        "property": fact.wikidata_property,
                        "question": meta_information.get("question"),
                        "wikipediaLink": wikipedia_link,
                        "wikidataLink": fact.wikidata_entity,
                        "text": evidence_highlight.get("text"),
                        "evidence": evidence,
                        "startIdx": evidence_highlight.get("startIdx"),
                        "endIdx": evidence_highlight.get("endIdx"),
                        "object": fact.data_value,
                    }
                )
        except Exception:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(custom_response, status=status.HTTP_200_OK)


class RetrieveRandomFactAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            pk_list = Fact.objects.values_list("pk", flat=True)
            random_pk = choice(pk_list)
            fact = Fact.objects.get(pk=random_pk)
            evidence_highlight = fact.evidence_highlight
            meta_information = fact.meta_information
            references = fact.references
            evidence, wikipedia_link = None, None  # setting default values
            for refer in references:
                if refer.get("type") == "string":
                    evidence = refer.get("value")
                elif refer.get("type") == "url":
                    wikipedia_link = refer.get("value")
            custom_response = {
                "id": fact.id,
                "property": fact.wikidata_property,
                "question": meta_information.get("question"),
                "wikipediaLink": wikipedia_link,
                "wikidataLink": fact.wikidata_entity,
                "text": evidence_highlight.get("text"),
                "evidence": evidence,
                "startIdx": evidence_highlight.get("startIdx"),
                "endIdx": evidence_highlight.get("endIdx"),
                "object": fact.data_value,
            }
        except Exception:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(custom_response, status=status.HTTP_200_OK)


class FactAcceptAPI(APIView):
    def post(self, request, *args, **kwargs):
        fact_id = request.data.get("fact_id")
        if not fact_id and not isinstance(fact_id, str):
            return Response(
                {"detail": "Invalid Fact ID."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            fact = Fact.objects.get(id=fact_id)
            feedback = {
                "value": True,
                "date": timezone.now(),
            }
            # to avoid TypeError: Object of type datetime is not JSON serializable
            feedback = json.dumps(feedback, cls=DjangoJSONEncoder)
            feedback = json.loads(feedback)
            fact.feedback = feedback
            fact.save()
        except Exception:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {"message": "Fact Accepted successfully"}, status=status.HTTP_200_OK
        )


class FactRejectAPI(APIView):
    def post(self, request, *args, **kwargs):
        fact_id = request.data.get("fact_id")
        if not fact_id and not isinstance(fact_id, str):
            return Response(
                {"detail": "Invalid Fact ID."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            fact = Fact.objects.get(id=fact_id)
            feedback = {
                "value": False,
                "date": timezone.now(),
            }
            # to avoid TypeError: Object of type datetime is not JSON serializable
            feedback = json.dumps(feedback, cls=DjangoJSONEncoder)
            feedback = json.loads(feedback)
            fact.feedback = feedback
            fact.save()
        except Exception:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {"message": "Fact Rejected successfully"}, status=status.HTTP_200_OK
        )
