import tls_client 
import random
import time
import uuid
import toml
import ctypes
import threading
import string

from collections import namedtuple
from faker import Faker
from Captcha_Wrapper.next import NextCaptchaAPI
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from logmagix import Logger, Home

with open('input/config.toml') as f:
    config = toml.load(f)

DEBUG = config['dev'].get('Debug', False)
log = Logger()

def debug(func_or_message, *args, **kwargs) -> callable:
    if callable(func_or_message):
        @wraps(func_or_message)
        def wrapper(*args, **kwargs):
            result = func_or_message(*args, **kwargs)
            if DEBUG:
                log.debug(f"{func_or_message.__name__} returned: {result}")
            return result
        return wrapper
    else:
        if DEBUG:
            log.debug(f"Debug: {func_or_message}")

def debug_response(response) -> None:
    debug(response.headers)
    debug(response.text)
    debug(response.status_code)

class Miscellaneous:
    @debug
    def get_proxies(self) -> dict:
        try:
            if config['dev'].get('Proxyless', False):
                return None
                
            with open('input/proxies.txt') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if not proxies:
                    log.warning("No proxies available. Running in proxyless mode.")
                    return None
                
                proxy_choice = random.choice(proxies)
                proxy_dict = {
                    "http": f"http://{proxy_choice}",
                    "https": f"http://{proxy_choice}"
                }
                log.debug(f"Using proxy: {proxy_choice}")
                return proxy_dict
        except FileNotFoundError:
            log.failure("Proxy file not found. Running in proxyless mode.")
            return None

    @debug 
    def generate_password(self) -> str:
        password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?/", k=16))
        return password
    
    @debug 
    def generate_username(self) -> str:
        return ''.join(random.choices(string.ascii_lowercase, k=16))
    
    @debug 
    def generate_email(self, domain: str = "bune.pw") -> str:
        username = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=20))}"
        email = f"{username}@{domain}"
        return email
    
    @debug 
    def randomize_user_agent(self) -> str:
        flipfit_build = random.randint(11900, 11999)
        cfnetwork_version = f"3826.{random.randint(300, 400)}.{random.randint(100, 200)}"
        darwin_version = f"24.{random.randint(1, 5)}.0"
        
        user_agent = f"flipfit/{flipfit_build} CFNetwork/{cfnetwork_version} Darwin/{darwin_version}"
        return user_agent

    
    @debug
    def solve_captcha(self, mode: str = "signUpByEmail") -> dict | None:
        try:
            api = NextCaptchaAPI(client_key=config['captcha']['NextCaptcha_Key'])
        except ValueError as e:
            print(f"Captcha API initialization failed: {e}")
            return None

        try:
            result = api.recaptcha_mobile(
                app_key="6LdejjsmAAAAALlBmYvDul0L8m6otWBomqkPQ_qS",
                app_package_name="com.flipfit.flip",
                app_action=mode,
                app_device="ios"
            )
            return result
        except Exception as e:
            print(f"Captcha solving failed: {e}")
            return None


    class Title:
        def __init__(self) -> None:
            self.running = False

        def start_title_updates(self, total, start_time) -> None:
            self.running = True
            def updater():
                while self.running:
                    self.update_title(total, start_time)
                    time.sleep(0.5)
            threading.Thread(target=updater, daemon=True).start()

        def stop_title_updates(self) -> None:
            self.running = False

        def update_title(self, total, start_time) -> None:
            try:
                elapsed_time = round(time.time() - start_time, 2)
                title = f'discord.cyberious.xyz | Total: {total} | Time Elapsed: {elapsed_time}s'

                sanitized_title = ''.join(c if c.isprintable() else '?' for c in title)
                ctypes.windll.kernel32.SetConsoleTitleW(sanitized_title)
            except Exception as e:
                log.debug(f"Failed to update console title: {e}")

class AccountCreator:
    def __init__(self, proxy_dict: dict) -> None:
        self.device_id = str(uuid.uuid4()).upper()
        self.anonymous_id = str(uuid.uuid4())
        self.RegisterResponse = namedtuple('RegisterResponse', ['AccessToken', 'deviceFingerprint'])

        self.session = tls_client.Session("mms_ios_3", random_tls_extension_order=True)
        self.session.headers = {
        'accept': 'application/json',
        'accept-language': 'fr-FR,fr;q=0.9',
        'app-platform': 'ios',
        'app-version': '6.4.2',
        'codepush-version': 'null',
        'connection': 'keep-alive',
        'content-type': 'application/json',
        'device-id': self.device_id,
        'host': 'api.flipfit.com',
        'user-agent': Miscellaneous().randomize_user_agent(),
        'x-anonymous-id': self.anonymous_id,
        }
        self.session.proxies = proxy_dict
       

    @debug
    def register(self, email: str, password: str) -> tuple | None:
        
        self.session.headers.update({ 
            'captcha-token': Miscellaneous().solve_captcha()["solution"]["gRecaptchaResponse"],
            'captcha-type': 'ios'
            })
        
        json_data = {
            'anonymousId': self.anonymous_id,
            'email': email,
            'password': password,
            'userStoreId': '63d918bfd516a2176fcaeb90',
        }

        response = self.session.post('https://api.flipfit.com/auth/email/signup/v1', json=json_data)

        debug_response(response)

        data = response.json()
        if response.status_code == 200 and data["data"]:

            self.session.headers.update({
                "authorization": f"Bearer {data['data']['auth']['accessToken']}",
                "device-fp": data["data"]["deviceFingerprint"]
            })
            
            self.session.headers.pop('captcha-token', None)
            self.session.headers.pop('captcha-type', None)

            return self.RegisterResponse(
                AccessToken=data["data"]["auth"]["accessToken"],
                deviceFingerprint=data["data"]["deviceFingerprint"]
            )
        else:
            log.failure(f"Failed to register account {response.text}, {response.status_code}")
            return None
    
    @debug
    def onboarding(self, username: str, bio: str = None) -> bool:
        debug("Starting onboarding process...")
        debug(f"Using headers: {self.session.headers}")
        
        # First name
        response = self.session.put('https://api.flipfit.com/api/user/me/v2', json={'name': f'{Faker().first_name()} '})
      
        debug_response(response)

        if response.status_code != 200:
            log.failure(f"Failed to update name {response.text}, {response.status_code}")
            return False

        # Last name
        response = self.session.put('https://api.flipfit.com/api/user/me/v2', json={"surname": f"{Faker().last_name()}"})
      
        debug_response(response)

        if response.status_code != 200:
            log.failure(f"Failed to update surname {response.text}, {response.status_code}")
            return False

        # Username
        response = self.session.put('https://api.flipfit.com/api/user/me/v2', json={"username": username })
              
        debug_response(response)

        if response.status_code != 200:
            log.failure(f"Failed to update username {response.text}, {response.status_code}")
            return False

        # First Date of Birth (also DOB)
        response = self.session.put('https://api.flipfit.com/api/user/me/v2', json={"dateOfBirth": f"{random.randint(1900, 2006)}-{str(random.randint(1, 12)).zfill(2)}-{str(random.randint(1, 28)).zfill(2)}T00:00:00.000Z" })
      
        debug_response(response)

        if response.status_code != 200:
            log.failure(f"Failed to update date of birth {response.text}, {response.status_code}")
            return False
        
        if bio:
            json_data = {
            'social': {
                'instagram': '',
                'tikTok': '',
            },
            'bioDescription': bio,
            }

            response = self.session.put('https://api.flipfit.com/api/user/me/v2', json=json_data)

            if response.status_code != 200:
                log.failure(f"Failed to update bio {response.text}, {response.status_code}")
                return False
              
            debug_response(response)
        
        return True


def create_account() -> bool:
    try:
        account_start_time = time.time()

        Misc = Miscellaneous()
        proxies = Misc.get_proxies()
        Account_Generator = AccountCreator(proxies)
        
        email = Misc.generate_email()
        username = Misc.generate_username()
        useBio = config["data"].get("useBio")
        password = config["data"].get("password") or Misc.generate_password()
        
        log.info(f"Starting a new account creation process for {email[:10]}...")
        account =  Account_Generator.register(email, password)

        if useBio:
            with open("input/data/bios.txt") as f:
                bios = [line.strip() for line in f if line.strip()]
                bio = random.choice(bios)

        if account:
           log.info("Successfully registered account. Starting onboarding...")
           if Account_Generator.onboarding(username, bio if useBio else None ):
                with open("output/accounts.txt", "a") as f:
                    f.write(f"{email}:{password}\n")

                with open("output/accounts_full_capture.txt", "a") as f:
                    f.write(f"{username}:{email}:{password}:{account.AccessToken}:{account.deviceFingerprint}\n")
                            
                log.message("Flip", f"Account created successfully: {email}... | {password[:8]}... | {username[:6]}... ", account_start_time, time.time())
                return True
               
        return False
    except Exception as e:
        log.failure(f"Error during account creation process: {e}")
        return False

def main() -> None:
    try:
        start_time = time.time()
        
        # Initialize basic classes
        Misc = Miscellaneous()
        Banner = Home("Flip Generator", align="center", credits="discord.cyberious.xyz")
        
        # Display Banner
        Banner.display()

        total = 0
        thread_count = config['dev'].get('Threads', 1)

        # Start updating the title
        title_updater = Misc.Title()
        title_updater.start_title_updates(total, start_time)
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            while True:
                futures = [
                    executor.submit(create_account)
                    for _ in range(thread_count)
                ]

                for future in as_completed(futures):
                    try:
                        if future.result():
                            total += 1
                    except Exception as e:
                        log.failure(f"Thread error: {e}")

    except KeyboardInterrupt:
        log.info("Process interrupted by user. Exiting...")
    except Exception as e:
        log.failure(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()