from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', views.ApiRegister.as_view(), name="user_register"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('flashcard/list/', views.FlashCardListAPIView.as_view(), name='flashcar_list' ),
    path('review/', views.ReviewAnswerAPIView.as_view(), name='review_answer')
]


"""
{
	"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NTA1MzU3MiwiaWF0IjoxNzI0MzE3NTcyLCJqdGkiOiIwMjhlNTA3NTEwOTY0Yjc2OGM2Y2FlMjkzMTkxMmY1NiIsInVzZXJfaWQiOjF9.o7ruVm_tLJB3AyIWhj8oUysilJihB7WOBvTjIgg1yk8",
	"access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI2OTA5NTcyLCJpYXQiOjE3MjQzMTc1NzIsImp0aSI6ImI2ZGY4MjBiODFkMjRlY2ZiMWZhY2JmNmY4Y2YxOGU1IiwidXNlcl9pZCI6MX0.O2CGda5HVNmGcQw_eWctuAZXmDclqFlhdSi9jTy9iKE"
}
"""