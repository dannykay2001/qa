from django.urls import path, include
from web import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("my_devices/", views.my_devices, name="my_devices"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("account/", views.account, name="account"),
    path("logout/", views.logout, name="logout"),
    path("change_status/<device_id>/<change_to>", views.change_status, name="change_status"),
    path("new_device/", views.new_device, name="new_device"),
    path("request_admin/", views.request_admin, name="request_admin"),
    path("transfers/", views.transfers, name="transfers"),
    path("transfer_response/<device_id>/<response>", views.transfer_response, name="transfer_response"),
    path("create_transfer/", views.create_transfer, name="create_transfer"),
    path("admin/", views.admin, name="admin")
]