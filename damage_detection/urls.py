from django.urls import path
from .views import DetectDamageView, OCRContainerView

urlpatterns = [
    path('detect/', DetectDamageView.as_view(), name='detect_damage'),
    path('ocr-container/', OCRContainerView.as_view(), name='ocr_container'),
]
