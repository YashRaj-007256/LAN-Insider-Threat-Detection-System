from rest_framework import generics
from .models import UserActivity
from .serializers import UserActivitySerializer
import ipaddress


def calculate_risk(data):
    event_type = data.get("event_type", "")
    destination_ip = data.get("destination_ip")

    risk_score = 0

    # System monitoring = low risk
    if event_type == "system_monitor":
        risk_score = 10

    # Network connection = base risk
    elif event_type == "network_connection":
        risk_score = 20

        # Check destination IP
        if destination_ip:
            try:
                ip = ipaddress.ip_address(destination_ip)

                # External/public destination
                if not ip.is_private and not ip.is_loopback:
                    risk_score += 30

            except ValueError:
                risk_score += 20

    # Other events
    else:
        risk_score = 30

    # Suspicious threshold
    is_suspicious = risk_score >= 50

    return risk_score, is_suspicious


class UserActivityListCreateView(generics.ListCreateAPIView):
    queryset = UserActivity.objects.all().order_by('-timestamp')
    serializer_class = UserActivitySerializer

    def perform_create(self, serializer):
        risk_score, is_suspicious = calculate_risk(self.request.data)

        serializer.save(
            risk_score=risk_score,
            is_suspicious=is_suspicious
        )