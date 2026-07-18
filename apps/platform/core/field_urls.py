from django.urls import path

from . import views

urlpatterns = [
    path("", views.field_dashboard, name="field-dashboard"),
    path("machines/new/", views.machine_create, name="machine-create"),
    path("events/new/", views.event_create, name="event-create"),
    path("events/<uuid:public_id>/", views.event_detail, name="event-detail"),
    path("events/<uuid:public_id>/captures/new/", views.capture_create, name="capture-create"),
    path("events/<uuid:public_id>/observations/new/", views.observation_create, name="observation-create"),
    path("events/<uuid:public_id>/hypotheses/new/", views.hypothesis_create, name="hypothesis-create"),
    path("events/<uuid:public_id>/decisions/new/", views.decision_create, name="decision-create"),
    path("events/<uuid:public_id>/outcome/", views.outcome_edit, name="outcome-edit"),
    path("events/<uuid:public_id>/unresolved/", views.unresolved_edit, name="event-unresolved"),
]
