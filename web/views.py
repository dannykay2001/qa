from django.shortcuts import render
from web.account_handling import AccountCreator, AccountHandler, LoginHandler
from web.device_handling import DeviceHandler, DeviceModelRetriever, UserDeviceRetriever
from .forms import AssignDeviceForm, LoginForm, PromoteAdminForm, RegisterForm

def home(request):
    return render(request, "web/home.html")

def about(request):
    return render(request, "web/about.html")

def admin(request):
    accounts = AccountHandler.get_all_accounts(request.session["user_id"])
    if request.session.has_key("logged_in") and request.session["logged_in"] and request.session["is_admin"]==True:
        if request.method == "POST":
            delete_success = True
            try:
                AccountHandler.delete_user_account(request.POST["user_id"])
                accounts = [account for account in accounts if account[0]!=int(request.POST["user_id"])]
            except:
                delete_success = False
            return render(request, "web/admin.html", {"accounts": accounts, "delete_success": delete_success})
        return render(request, "web/admin.html", {"accounts": accounts})
    return render(request, "web/admin.html" )

def my_devices(request, models=None, assign_status=None):
    if request.session.has_key("logged_in") and request.session["logged_in"]:
        devices = UserDeviceRetriever.get_user_devices(request.session["user_id"])
        if len(devices) == 0:
            return render_my_devices_page(request, no_devices=True, models=models, assign_status=assign_status)
        else:
            return render_my_devices_page(request, user_devices=devices, models=models, assign_status=assign_status)
    else:
        return render_my_devices_page(request)

def new_device(request):
    if request.method == 'POST':
        form = AssignDeviceForm(request.POST)
        try:
            DeviceHandler.assign_new_device(form.data["device_id"], request.session["user_id"], form.data["model_id"])
            return my_devices(request, assign_status=1)
        except:
            models = DeviceModelRetriever.get_all_models()
            return my_devices(request, assign_status=-1, models=models)
    form = AssignDeviceForm()
    models = DeviceModelRetriever.get_all_models()
    return my_devices(request, models=models)

def change_status(request, device_id, change_to):
    DeviceHandler.change_device_status(device_id, change_to)
    return my_devices(request)

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if LoginHandler.attempt_login(request, form.data['email'], form.data['password']):
            return render(request, "web/home.html")
        else:
            return render_login_page(request, login_failed=True)
    return render_login_page(request)

def logout(request):
    keys = ["logged_in", "user_id", "user_display_name", "user_email", "is_admin"]
    for key in keys:
        if request.session.has_key(key):
            del request.session[key]
    return render(request, "web/home.html")

def request_admin(request):
    if request.method == 'POST':
        promote_admin_button = request.POST.get("admin_button")
        admin_form = PromoteAdminForm(request.POST)
        if not admin_form.is_correct():
            return render_account_page(request, request_admin = True, request_admin_password_incorrect = True)
        else:
            AccountHandler.promote_user_admin(request.session['user_id'])
            request.session['is_admin'] = True
            return render_account_page(request, request_admin_success = True)
    return render_account_page(request, True)

def account(request):
    return render_account_page(request)

def register(request):
    if request.method == 'POST':
        account_creator = AccountCreator()
        form = RegisterForm(request.POST)
        invalid_fields = form.validate_form()
        if form.invalid_flag:
            return render_register_page(request, *invalid_fields)
        if AccountCreator.user_exists(form.data['email']):
            return render_register_page(request, email_in_use=True)
        else:
            if AccountCreator.attempt_create_user(form.data['name'], form.data['email'], form.data['password'], False) == 1:
                return render(request, "web/about.html")
            else:
                return render_register_page(request, sql_error=True)
    return render(request, "web/register.html")

def transfers(request, incoming_response_error=None, new_tranfer_request_success=None, devices=None, same_email_error=None):
    # logger.error([row[:2] for row in UserDeviceRetriever.get_user_devices(request.session["user_id"])])
    if request.session.has_key("logged_in") and request.session["logged_in"]:
        incoming_transfers = DeviceHandler.get_incoming_transfers(request.session["user_id"])
        outgoing_transfers = DeviceHandler.get_outgoing_transfers(request.session["user_id"])
        return render(request, "web/transfers.html", {"incoming_transfers": incoming_transfers, "incoming_response_error": incoming_response_error, "new_tranfer_request_success": new_tranfer_request_success, "devices":devices, "same_email_error":same_email_error, "outgoing_transfers": outgoing_transfers})

    return render(request, "web/transfers.html")

def create_transfer(request):
    devices = [row[:2] for row in UserDeviceRetriever.get_user_devices(request.session["user_id"], exclude_open_transfers=True)]
    if request.method == 'POST':
        # if request.POST.has_key("device_id") and request.POST.has_key("new_owner_email"):
        if "device_id" in request.POST and "new_owner_email" in request.POST:
            if request.POST["new_owner_email"] == request.session["user_email"]:
                return transfers(request, devices=devices, same_email_error=True)
            try:
                DeviceHandler.create_transfer(request.POST["device_id"], request.session["user_id"], request.POST["new_owner_email"])
                return transfers(request, new_tranfer_request_success=True)
            except:
                return transfers(request, devices=devices, new_tranfer_request_success=False)
        else:
            return transfers(request, new_tranfer_request_success=False)

    return transfers(request, devices=devices)

def transfer_response(request, device_id, response):
    try:
        if response == "DECLINE":
            DeviceHandler.decline_transfer(device_id)
        elif response == "ACCEPT":
            DeviceHandler.accept_transfer(device_id, request.session["user_id"])
        return transfers(request, incoming_response_error=False)
    except:
        return transfers(request, incoming_response_error=True)

def render_account_page(request, request_admin = None, request_admin_password_incorrect = None, request_admin_success = None):
    return render(request, "web/account.html", {"request_admin": request_admin, "request_admin_password_incorrect": request_admin_password_incorrect, "request_admin_success": request_admin_success})

def render_register_page(request, email_invalid = None, name_invalid = None, password_invalid = None, password_no_match = None, email_in_use = None, sql_error = None):
    return render(request, "web/register.html", {"email_invalid": email_invalid, "name_invalid": name_invalid, "password_invalid": password_invalid, "password_no_match": password_no_match, "email_in_use": email_in_use, "sql_error":sql_error})

def render_login_page(request, login_failed = None):
    return render(request, "web/login.html", {"login_failed": login_failed})

def render_my_devices_page(request, no_devices = None, user_devices = None, assigning_device=None, models=None, assign_status=None):
    return render(request, "web/my_devices.html", {"no_devices": no_devices, "user_devices": user_devices, "assigning_device": assigning_device, "models": models, "assign_status": assign_status})