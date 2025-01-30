import requests
from Captcha_Wrapper.next import NextCaptchaAPI

def solve_captcha(mode: str = "signUpByEmail"):
        try:
            api = NextCaptchaAPI(client_key="next_28a82ff0f0af69164eed38f21a0f03289e")
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

headers = {
    'accept': 'application/json',
    'accept-language': 'fr-FR,fr;q=0.9',
    'app-platform': 'ios',
    'app-version': '6.4.2',
    'baggage': 'sentry-environment=production,sentry-public_key=833f68145f3842f98191eb7a8455aafc,sentry-trace_id=e40d8fc1e74343b8a1b4c1d29db959ad',
    'captcha-token': solve_captcha()["solution"]["gRecaptchaResponse"],
    'captcha-type': 'ios',
    'codepush-version': 'undefined',
    'connection': 'keep-alive',
    'content-type': 'application/json',
    'device-id': '1F181E0E-5DB6-47AF-81DD-4525FF7DE72F',
    'host': 'api.flipfit.com',
    'sentry-trace': 'e40d8fc1e74343b8a1b4c1d29db959ad-bf50dd94a6a497d3',
    'user-agent': 'flipfit/11919 CFNetwork/3826.400.110 Darwin/24.3.0',
    'x-anonymous-id': 'efe86a81-a8cd-4368-a7d8-48bc767e606c',
}

json_data = {
    'anonymousId': 'efe86a81-a8cd-4368-a7d8-48bc767e606c',
    'email': 'asadsasd@bune.pw',
    'password': 'Noah2009!',
    'userStoreId': '63d918bfd516a2176fcaeb90',
}

response = requests.post('https://api.flipfit.com/auth/email/signup/v1', headers=headers, json=json_data)
print(response.text)