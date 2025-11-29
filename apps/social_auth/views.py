from rest_framework.views import APIView
from apps.utils.helpers import success 
from apps.social_auth.serializers import GoogleSerializer

from apps.utils.helpers import success, error


class GoogleLoginAPIView(APIView):
    def post(self,request):

        serializer = GoogleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = (serializer.validated_data)['access_token']

            return success(
                data=data,
                message="Login successful.",
                status_code=200
            )
        return error(message="Login failed.",status_code=400,errors=serializer.errors)