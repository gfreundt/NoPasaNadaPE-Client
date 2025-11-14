import requests
import string
import random
import json
import time


class TempEmail:

    def __init__(self, log):
        self.log = log
        self.API_BASE_URL = "https://api.mail.tm"

    def get_temp_email(self):
        domain = self.get_available_domain()
        if not domain:
            return None

        self.username, self.password = self.generate_random_credentials()
        account_data = self.create_temp_email_account(
            domain, self.username, self.password
        )

        if account_data:
            self.email_address = account_data.get("address")
            self.account_id = account_data.get("id")

            # Login to get the JWT token, required for fetching emails
            self.jwt_token = self.login_and_get_token(self.email_address, self.password)

            return {
                "email_address": self.email_address,
                "password": self.password,  # IMPORTANT: You need the password for subsequent logins/token renewal
                "account_id": self.account_id,
                "token": self.jwt_token,
            }

        return None

    def generate_random_credentials(self, length=10):
        """Generate a random username and a strong password."""
        chars = string.ascii_letters + string.digits
        # Generate a random username (prefix)
        username = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
        # Generate a strong password
        password = "".join(random.choice(chars) for _ in range(length)) + random.choice(
            string.punctuation
        )
        return username, password

    def get_available_domain(self):
        """Fetches a list of available domains from the Mail.tm API."""
        url = f"{self.API_BASE_URL}/domains"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            domains = response.json().get("hydra:member")

            if domains:
                # Pick a random domain from the list
                return random.choice(domains)["domain"]
            else:
                self.log(action="Error: No domains found in API response.")
                return None
        except requests.exceptions.RequestException as e:
            self.log(action=f"Error fetching domains: {e}")
            return None

    def create_temp_email_account(self, domain, username, password):
        """Creates a new temporary email account and returns the account details."""
        url = f"{self.API_BASE_URL}/accounts"
        headers = {"Content-Type": "application/json"}
        payload = {"address": f"{username}@{domain}", "password": password}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            account_data = response.json()
            return account_data
        except requests.exceptions.RequestException as e:
            self.log(action=f"Error creating account: {e}")
            self.log(
                action=f"Response content: {response.text if 'response' in locals() else 'N/A'}"
            )
            return None

    def login_and_get_token(self, email_address, password):
        """Logs into the newly created account to get a JWT access token."""
        url = f"{self.API_BASE_URL}/token"
        headers = {"Content-Type": "application/json"}
        payload = {"address": email_address, "password": password}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            token_data = response.json()
            token = token_data.get("token")
            return token
        except requests.exceptions.RequestException as e:
            self.log(action=f"Error logging in: {e}")
            self.log(
                action=f"Response content: {response.text if 'response' in locals() else 'N/A'}"
            )
            return None

    def wait_for_new_email(self, jwt_token, timeout=60, interval=5):
        start_time = time.time()
        url = f"{self.API_BASE_URL}/messages"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {jwt_token}",
        }

        self.log(
            action=f"Esperando correo... (Timeout in {timeout} seconds, checking every {interval}s)"
        )

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                response_data = response.json()
                messages = []

                if isinstance(response_data, dict):
                    # Handles the case where the response is a dictionary containing 'hydra:member'
                    messages = response_data.get("hydra:member", [])
                elif isinstance(response_data, list):
                    # Handles the case where the response is a direct list of messages
                    messages = response_data

                if messages:
                    # Assuming the API returns messages newest first
                    self.log(action="✅ Correo recibido!")
                    latest_message = messages[0]
                    return latest_message.get("intro")

                time.sleep(interval)

            except requests.exceptions.HTTPError as e:
                self.log(
                    action=f"   HTTP Error fetching messages: {e}. Response: {response.text}"
                )
                time.sleep(interval)
            except requests.exceptions.RequestException as e:
                self.log(action=f"   Connection Error: {e}. Retrying...")
                time.sleep(interval)
            except json.JSONDecodeError:
                self.log(
                    action="   JSON Decode Error: Response was not valid JSON. Retrying..."
                )
                time.sleep(interval)

        self.log(
            action=f"\n❌ Timeout reached. No email received within {timeout} seconds."
        )
        return None
