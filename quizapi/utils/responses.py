from rest_framework import status
from rest_framework.response import Response


def response_400(detail):
    """
    Returns rest_framework.response.Response object
    with HTTP_400_BAD_REQUEST status and detail information.
    """
    return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)


def response_404(detail='Not found'):
    """
    Returns rest_framework.response.Response object
    with HTTP_404_BAD_REQUEST status and detail information.
    """
    return Response({'detail': detail}, status=status.HTTP_404_NOT_FOUND)