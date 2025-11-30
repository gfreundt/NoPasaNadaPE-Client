import requests
import json

# from google.cloud import billingbudgets_v1
from src.utils.constants import (
    TRUECAPTCHA_API_KEY,
    BRIGHT_DATA_API_KEY,
    GC_BILLING_ACCOUNT_ID,
    GC_BUDGET_ID,
    TWOCAPTCHA_API_KEY,
)


def get_truecaptcha():
    try:
        url = rf"https://api.apiTruecaptcha.org/one/hello?method=get_all_user_data&userid=gabfre%40gmail.com&apikey={TRUECAPTCHA_API_KEY}"
        r = requests.get(url)
        return f'✅ USD {r.json()["data"]["get_user_info"][4]["value"]:.2f}'
    except Exception:
        return "❓ N/A"


def get_zeptomail():
    return "❓ N/A"


def get_brightdata():
    return "❓ N/A"

    BALANCE_URL = "https://api.brightdata.com/balance"
    headers = {
        "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(BALANCE_URL, headers=headers)
        if response.status_code == 200:
            balance_data = response.json()
            balance = balance_data.get("balance")
            currency = balance_data.get("currency")
            if balance and currency:
                return f"{currency} {balance}"

        return "N/A"

    except requests.exceptions.RequestException:
        return "N/A"


def get_googlecloud():

    return "❓ N/A"

    client = billingbudgets_v1.BudgetServiceClient()
    name = f"billingAccounts/{GC_BILLING_ACCOUNT_ID}/budgets/{GC_BUDGET_ID}"

    try:
        budget = client.get_budget(name=name)
        if budget.amount.last_period_amount is not None:
            summary = budget.budgeted_amount_summary
            spend_money = summary.current_budget_spend
            actual_spend = spend_money.units + spend_money.nanos / 1e9
            currency = spend_money.currency_code
            return f"{currency} {actual_spend:.2f}"
        else:
            return "⚠️ N/A"

    except Exception:
        return "❓ N/A"


def get_2captcha():

    URL = f"https://2captcha.com/res.php?key={TWOCAPTCHA_API_KEY}&action=getbalance"

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        result = response.text

        if result.startswith("ERROR_"):
            return "❓ N/A"
        else:
            try:
                balance = float(result)
                return f"✅ USD {balance:.2f}"
            except ValueError:
                return "❓ N/A"

    except requests.exceptions.RequestException:
        return "❓ N/A"


def get_cloudfare():
    return "✅ ACTIVO"


def main():

    return {
        "kpi_truecaptcha_balance": get_truecaptcha(),
        "kpi_zeptomail_balance": get_zeptomail(),
        "kpi_brightdata_balance": get_brightdata(),
        "kpi_twocaptcha_balance": get_2captcha(),
        "kpi_googlecloud_balance": get_googlecloud(),
        "kpi_cloudfare_balance": get_cloudfare(),
    }
