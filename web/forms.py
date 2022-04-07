from asyncio.log import logger
from cProfile import label
from django import forms
import re

from web.device_handling import DeviceModelRetriever

class AssignDeviceForm(forms.Form):
    model_id = forms.SelectMultiple(choices=DeviceModelRetriever.get_all_models())
    device_id = forms.CharField(label="device_id")

class RegisterForm(forms.Form):
    email = forms.CharField(label="email")
    name = forms.CharField(label="name")
    password = forms.CharField(label="password")
    confirm_password = forms.CharField(label="confirm_password")

    invalid_flag = False

    def validate_form(self):
        email_invalid = name_invalid = password_invalid = password_no_match = False
        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', self.data['email']):
            email_invalid = True
            self.invalid_flag = True
        if not re.fullmatch(r'^[a-zA-Z]+$', self.data['name']):
            name_invalid = True
            self.invalid_flag = True
        if re.search(r'[0-9]', self.data['password']) is None:
            password_invalid = True
            self.invalid_flag = True
        if self.data['password'] != self.data['confirm_password']:
            password_no_match = True
            self.invalid_flag = True
        return (email_invalid, name_invalid, password_invalid, password_no_match)

class LoginForm(forms.Form):
    email = forms.CharField(label="email")
    password = forms.CharField(label="password")

class PromoteAdminForm(forms.Form):
    admin_password = forms.CharField(label="admin_password")

    def is_correct(self):
        if self.data['admin_password'] == "password":
            return True
        return False