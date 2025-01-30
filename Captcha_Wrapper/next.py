from logmagix import Logger, LogLevel
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
import urllib3



RECAPTCHAV2_TYPE = "RecaptchaV2TaskProxyless"
RECAPTCHAV2_ENTERPRISE_TYPE = "RecaptchaV2EnterpriseTaskProxyless"
RECAPTCHAV2HS_ENTERPRISE_TYPE = "RecaptchaV2HSEnterpriseTaskProxyless"
RECAPTCHAV3_PROXYLESS_TYPE = "RecaptchaV3TaskProxyless"
RECAPTCHAV3HS_PROXYLESS_TYPE = "RecaptchaV3HSTaskProxyless"
RECAPTCHAV3_TYPE = "RecaptchaV3Task"
RECAPTCHA_MOBILE_PROXYLESS_TYPE = "ReCaptchaMobileTaskProxyLess"
RECAPTCHA_MOBILE_TYPE = "ReCaptchaMobileTask"
HCAPTCHA_TYPE = "HCaptchaTask"
HCAPTCHA_PROXYLESS_TYPE = "HCaptchaTaskProxyless"
HCAPTCHA_ENTERPRISE_TYPE = "HCaptchaEnterpriseTask"

TIMEOUT = 45

PENDING_STATUS = "pending"
PROCESSING_STATUS = "processing"
READY_STATUS = "ready"
FAILED_STATUS = "failed"


class TaskBadParametersError(Exception):
    pass
   
class ApiClient:
    HOST = "https://api.nextcaptcha.com"

    def __init__(self, client_key: str, solft_id: str, callback_url: str, open_log: bool, log_level: str = "INFO") -> None:
        self.client_key = client_key
        self.log = Logger(level=LogLevel[log_level])
        self.solft_id = solft_id
        self.callback_url = callback_url
        self.open_log = open_log
        self.session = requests.session()

        adapter = HTTPAdapter(pool_maxsize=1000)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        urllib3.disable_warnings()

    def _get_balance(self) -> str:
        resp = self.session.post(url=self.HOST + "/getBalance", json={"clientKey": self.client_key})
        if resp.status_code != 200:
            if self.open_log:
                self.log.failure(f"Error: {resp.status_code} {resp.text}")
            return resp.json()
        if self.open_log:
            self.log.info(f"Balance: {resp.json().get('balance')}")
        return resp.json().get("balance")

    def _send(self, task: dict) -> dict:
        data = {
            "clientKey": self.client_key,
            "softId": self.solft_id,
            "callbackUrl": self.callback_url,
            "task": task,
        }
      
        resp = self.session.post(url=self.HOST + "/createTask", json=data)
        if resp.status_code != 200:
            if self.open_log:
                self.log.failure(f"Error: {resp.status_code} {resp.text}")
                self.log.failure(f"Data: {data}")
            return resp.json()
        resp = resp.json()
        task_id = resp.get("taskId")
        if self.open_log:
            self.log.debug(f"Task {task_id} created {resp}")

        start_time = time.time()
        while True:
            if time.time() - start_time > TIMEOUT:
                return {"errorId": 12, "errorDescription": "Timeout", "status": "failed"}

            resp = self.session.post(url=self.HOST + "/getTaskResult",
                                     json={"clientKey": self.client_key, "taskId": task_id})
            if resp.status_code != 200:
                if self.open_log:
                    self.log.failure(f"Error: {resp.status_code} {resp.text}")
                return resp.json()
            status = resp.json().get("status")
            if self.open_log:
                self.log.debug(f"Task status: {status}")
            if status == READY_STATUS:
                if self.open_log:
                    self.log.debug(f"Task {task_id} ready {resp.json()}")
                return resp.json()
            if status == FAILED_STATUS:
                if self.open_log:
                    self.log.failure(f"Task {task_id} failed {resp.json()}")
                return resp.json()
            time.sleep(0.5)


class NextCaptchaAPI:
    def __init__(self, client_key: str, solft_id: str = "", callback_url: str = "", open_log: bool = True, log_level: str = "INFO") -> None:
        self.log = Logger(level=LogLevel[log_level])
        self.log.debug(
            f"NextCaptchaAPI created with clientKey={client_key} solftId={solft_id} callbackUrl={callback_url}")
        self.api = ApiClient(client_key=client_key, solft_id=solft_id, callback_url=callback_url, open_log=open_log)

    def recaptcha_mobile(self, app_key: str, app_package_name: str = "", app_action: str = "", proxy_type: str = "",
                         proxy_address: str = "", proxy_port: int = 0, proxy_login: str = "",
                         proxy_password: str = "", app_device: str = "android") -> dict:

        task = {
            "type": RECAPTCHA_MOBILE_PROXYLESS_TYPE,
            "appKey": app_key,
            "appPackageName": app_package_name,
            "appAction": app_action,
            "appDevice": app_device,
        }
        if proxy_address != "":
            task["type"] = RECAPTCHA_MOBILE_TYPE
            task["proxyType"] = proxy_type
            task["proxyAddress"] = proxy_address
            task["proxyPort"] = proxy_port
            task["proxyLogin"] = proxy_login
            task["proxyPassword"] = proxy_password
        return self.api._send(task)

    def recaptchav2(self, website_url: str, website_key: str, recaptcha_data_s_value: str = "",
                    is_invisible: bool = False, api_domain: str = "", page_action: str = "",
                    website_info: str = "") -> dict:
        """
        Solve reCAPTCHA v2 challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :param recaptcha_data_s_value: Optional. The value of the 'data-s' parameter if present.
        :param is_invisible: Optional. Whether the reCAPTCHA is invisible or not.
        :param api_domain: Optional. The domain of the reCAPTCHA API if different from the default.
        :return: A dictionary containing the solution of the reCAPTCHA.
        """
        task = {
            "type": RECAPTCHAV2_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
            "recaptchaDataSValue": recaptcha_data_s_value,
            "isInvisible": is_invisible,
            "apiDomain": api_domain,
            "pageAction": page_action,
            "websiteInfo": website_info
        }
        return self.api._send(task)

    def recaptchav3(self, website_url: str, website_key: str, page_action: str = "", api_domain: str = "",
                    proxy_type: str = "", proxy_address: str = "", proxy_port: int = 0, proxy_login: str = "",
                    proxy_password: str = "", website_info: str = "") -> dict:
        """
        Solve reCAPTCHA v3 challenge.

        :param website_url: The URL of the website where the reCAPTCHA is located.
        :param website_key: The sitekey of the reCAPTCHA.
        :param page_action: Optional. The action parameter to use for the reCAPTCHA.
        :param api_domain: Optional. The domain of the reCAPTCHA API if different from the default.
        :param proxy_type: Optional. The type of the proxy (HTTP, HTTPS, SOCKS4, SOCKS5).
        :param proxy_address: Optional. The address of the proxy.
        :param proxy_port: Optional. The port of the proxy.
        :param proxy_login: Optional. The login for the proxy.
        :param proxy_password: Optional. The password for the proxy.
        :return: A dictionary containing the solution of the reCAPTCHA.
        """
        task = {
            "type": RECAPTCHAV3_PROXYLESS_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
            "pageAction": page_action,
            "apiDomain": api_domain,
            "websiteInfo": website_info

        }
        if proxy_address:
            task["type"] = RECAPTCHAV3_TYPE
            task["proxyType"] = proxy_type
            task["proxyAddress"] = proxy_address
            task["proxyPort"] = proxy_port
            task["proxyLogin"] = proxy_login
            task["proxyPassword"] = proxy_password
        return self.api._send(task)

    def get_balance(self) -> str:
        return self.api._get_balance()