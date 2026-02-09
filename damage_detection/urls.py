from django.urls import path
from .views import DetectDamageView

urlpatterns = [
    path('detect/', DetectDamageView.as_view(), name='detect_damage'),
]
