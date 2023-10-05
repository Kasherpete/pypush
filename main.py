import json
import logging
import threading
import time
from base64 import b64decode, b64encode

from utils import apns, ids, imessage


def safe_b64decode(s):
    try:
        return b64decode(s)
    except:
        return None


def fixup_handle(handle):
    if handle.startswith('tel:+'):
        return handle
    elif handle.startswith('mailto:'):
        return handle
    elif handle.startswith('tel:'):
        return 'tel:+' + handle[4:]
    elif handle.startswith('+'):
        return 'tel:' + handle
    # If the handle starts with a number
    elif handle[0].isdigit():
        # If the handle is 10 digits, assume it's a US number
        if len(handle) == 10:
            return 'tel:+1' + handle
        # If the handle is 11 digits, assume it's a US number with country code
        elif len(handle) == 11:
            return 'tel:+' + handle
    else:  # Assume it's an email
        return 'mailto:' + handle


class Client:

    def __init__(self, config=None):

        if config is None:
            self.logged_in = False
            self.config = {}

        else:
            self.logged_in = True
            self.config = config

            self._apns_connect()

            auth_keypair = ids._helpers.KeyPair(self.config["auth"]["key"], self.config["auth"]["cert"])
            user_id = self.config["auth"]["user_id"]
            handles = self.config["auth"]["handles"]
            self.user.restore_authentication(auth_keypair, user_id, handles)

            self._apns_validate()

    def _apns_connect(self):

        self.conn = apns.APNSConnection(
            self.config.get("push", {}).get("key"), self.config.get("push", {}).get("cert")
        )

        self.conn.connect(token=safe_b64decode(self.config.get("push", {}).get("token")))
        self.conn.set_state(1)
        self.conn.filter(["com.apple.madrid"])

        self.user = ids.IDSUser(self.conn)

    def login(self, username: str, password: str):

        if not self.logged_in:

            self.username = username
            self.password = password

            self._apns_connect()
            self.auth_code = None

            threading.Thread(target=self.user.authenticate, args=(self.username, self.password, self._retrieve_auth_code), daemon=True).start()

    def _retrieve_auth_code(self, required: bool):

        if required:
            print('waiting...')

            while True:
                if self.auth_code is not None:
                    return self.auth_code
                time.sleep(.2)

        else:
            return

    def authenticate(self, code=None):

        if code is not None:
            self.auth_code = code

        self.logged_in = True

        try:
            self._apns_validate()
        except:
            print('NEED AUTH CODE!')
            exit(-1)

    def _apns_validate(self):

        self.user.encryption_identity = ids.identity.IDSIdentity(
            encryption_key=self.config.get("encryption", {}).get("rsa_key"),
            signing_key=self.config.get("encryption", {}).get("ec_key"),
        )

        if (
                self.config.get("id", {}).get("cert") is not None
                and self.user.encryption_identity is not None
        ):
            id_keypair = ids._helpers.KeyPair(self.config["id"]["key"], self.config["id"]["cert"])
            self.user.restore_identity(id_keypair)
        else:
            logging.info("Registering new identity...")
            from utils.emulated import nac

            vd = nac.generate_validation_data()
            vd = b64encode(vd).decode()

            self.user.register(vd)

        self.config["encryption"] = {
            "rsa_key": self.user.encryption_identity.encryption_key,
            "ec_key": self.user.encryption_identity.signing_key,
        }
        self.config["id"] = {
            "key": self.user._id_keypair.key,
            "cert": self.user._id_keypair.cert,
        }
        self.config["auth"] = {
            "key": self.user._auth_keypair.key,
            "cert": self.user._auth_keypair.cert,
            "user_id": self.user.user_id,
            "handles": self.user.handles,
        }
        self.config["push"] = {
            "token": b64encode(self.user.push_connection.token).decode(),
            "key": self.user.push_connection.private_key,
            "cert": self.user.push_connection.cert,
        }

        self.im = imessage.iMessageUser(self.conn, self.user)

    def get_incoming_message(self):

        return self.im.receive()

    def get_handles(self):

        return {'current': self.user.current_handle, 'all': self.user.handles}

    def set_handle(self, handle):

        if handle in self.user.handles:
            self.user.current_handle = fixup_handle(handle)
        else:
            print(f'Handle "{handle}" not found!')

    def send_message(self, to, content, sender=None, effect=None):

        if sender is None:
            sender = self.user.current_handle

        if type(to) is str:
            to = [to]

        to = [fixup_handle(h) for h in to]

        print(to)

        self.im.send(imessage.iMessage(
            text=content,
            participants=to,
            sender=sender,
            effect=effect
        ))

    def load_config_file(self, filepath: str, update: bool = True):

        self.config = json.loads(open(filepath, 'r').read())
        self._apns_connect()

        self.logged_in = True

        auth_keypair = ids._helpers.KeyPair(self.config["auth"]["key"], self.config["auth"]["cert"])
        user_id = self.config["auth"]["user_id"]
        handles = self.config["auth"]["handles"]
        self.user.restore_authentication(auth_keypair, user_id, handles)

        self._apns_validate()

        if update:
            open(filepath, 'w').write(json.dumps(self.config))

