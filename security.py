from resources.admin import AdminModel
import hmac


def authenticate(name, password):
    try:
        admin = AdminModel.find_by_name(name)
        if admin and hmac.compare_digest(admin.password, password):
            return admin
    except:
        return None


def identity(payload):
    _id = payload['identity']
    try:
        return AdminModel.find_by_id(_id)
    except:
        return None
