from django.urls import path
from . import views

urlpatterns = [
    # existing steps
    path("add/step1/", views.structure_step1, name="structure_step1"),
    path("add/step2/", views.structure_step2, name="structure_step2"),
    path("add/step3/", views.structure_step3, name="structure_step3"),
    path("add/step4/", views.structure_step4, name="structure_step4"),

    # existing features
    path("list/", views.structure_list, name="structure_list"),
    path("search/", views.structure_search, name="structure_search"),

    # 🆕 NEW: DETAIL VIEW
    path("view/<str:ts_id>/", views.structure_detail, name="structure_detail"),

    # 🆕 NEW: PAYMENT SYSTEM
    path("payment/<str:ts_id>/", views.record_payment_session, name="record_payment_session"),

    # 🆕 NEW: EDIT REQUEST SYSTEM
    path("edit/<str:ts_id>/", views.request_edit, name="request_edit"),

]