from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from utils.permissions import IsAdminUser
from .models import KYCDocument
from .serializers import KYCDocumentSerializer

class KYCSubmitView(generics.CreateAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['KYC'], summary='Submit KYC documents')
    def perform_create(self, serializer):
        KYCDocument.objects.filter(user=self.request.user).delete()
        serializer.save(user=self.request.user)

class KYCStatusView(generics.RetrieveAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['KYC'], summary='Get my KYC status')
    def get_object(self):
        obj, _ = KYCDocument.objects.get_or_create(
            user=self.request.user,
            defaults={'doc_type': KYCDocument.DocType.NATIONAL_ID}
        )
        return obj

class AdminKYCListView(generics.ListAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsAdminUser]
    queryset = KYCDocument.objects.select_related('user').all()

    @extend_schema(tags=['KYC'], summary='List all KYC submissions (admin)')
    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

class AdminKYCActionView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['KYC'], summary='Approve or reject KYC (admin)',
        request=inline_serializer('KYCAction', fields={
            'action': serializers.ChoiceField(choices=['approve','reject']),
            'rejection_reason': serializers.CharField(required=False, allow_blank=True),
        }),
        responses={200: KYCDocumentSerializer()},
    )
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        kyc = get_object_or_404(KYCDocument, pk=pk)
        action = request.data.get('action')
        if action == 'approve':
            kyc.status = KYCDocument.Status.APPROVED
            kyc.rejection_reason = ''
        elif action == 'reject':
            kyc.status = KYCDocument.Status.REJECTED
            kyc.rejection_reason = request.data.get('rejection_reason', '')
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
        kyc.reviewed_at = timezone.now()
        kyc.save()
        return Response(KYCDocumentSerializer(kyc).data)
