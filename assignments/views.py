from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Assignment, Submission
from .serializers import (
    AssignmentSerializer,
    SubmissionSerializer,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            student=self.request.user.student
        )

    def get_queryset(self):
        user = self.request.user

        # Student sees only their submissions
        if hasattr(user, "student"):
            return Submission.objects.filter(
                student=user.student
            )

        # Teacher/admin can see all submissions
        return Submission.objects.all()