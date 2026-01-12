from apps.system_setting.models import AboutSystem
from rest_framework.views import APIView
from apps.system_setting.serializers import AboutSystemSerializer
from apps.utils.helpers import success, error
# Create your views here.   

class AboutSystemAPIView(APIView):
    permission_classes = []
    def get(self, request):

        about_system = AboutSystem.objects.first()
   
        if about_system:
            serializer = AboutSystemSerializer(about_system)
            return success(serializer.data, "About system retrieved successfully.",200)
        return error(message="About system not found.", errors=None, status_code=404)
