
TRANSACTION_FIELDS = [
    "transaction_id",
    "customer_id",
    "amount",
    "currency",
    "transaction_ts",
    "status"
]

REQUIRED_FIELDS = [
    "transaction_id",
    "customer_id",
    "amount",
    "currency",
    "transaction_ts",
    "status"
]

ALLOWED_CURRENCIES = {"INR", "USD", "EUR"}

ALLOWED_STATUSES = {
    "completed",
    "pending",
    "refunded"
}

# Transaction amount categories
SMALL_AMOUNT_LIMIT = 1000
MEDIUM_AMOUNT_LIMIT = 10000


def get_amount_category(amount):
    if amount < SMALL_AMOUNT_LIMIT:
        return "small"
    elif amount < MEDIUM_AMOUNT_LIMIT:
        return "medium"
    return "large"
