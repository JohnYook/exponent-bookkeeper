from enum import StrEnum


class AccountType(StrEnum):
    CARD = "CARD"
    BANK = "BANK"


class TransactionType(StrEnum):
    PURCHASE = "purchase"
    REFUND = "refund"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"


class Category(StrEnum):
    FOOD_BEV = "Food & beverage"
    UTILITIES = "Utilities"
    REPAIRS = "Repairs & maintenance"
    CLEANING = "Cleaning & supplies"
    SMALLWARE = "Smallwares & supplies"
    PAYROLL = "Payroll"
    HIRING = "Hiring"
    SOFTWARE = "Software"
    RENT = "Rent"
    CARD_SALES = "Card sales"
    DELIVERY = "Delivery sales"
    UNCATEGORIZED = "Uncategorized"


MERCHANT_CATEGORIES = {
    "SYSCO": Category.FOOD_BEV,
    "US FOODS": Category.FOOD_BEV,
    "RESTAURANT DEPOT": Category.FOOD_BEV,
    "METRO GAS & ELECTRIC": Category.UTILITIES,
    "CITY WATER DEPT": Category.UTILITIES,
    "COMCAST BUSINESS": Category.UTILITIES,
    "HOME DEPOT": Category.REPAIRS,
    "ECOLAB": Category.CLEANING,
    "WEBSTAURANT STORE": Category.SMALLWARE,
    "GUSTO": Category.PAYROLL,
    "INDEED": Category.HIRING,
    "7SHIFTS": Category.SOFTWARE,
    "MAINLINE PROPERTIES": Category.RENT,
    "TOAST PAYOUT": Category.CARD_SALES,
    "DOORDASH PAYOUT": Category.DELIVERY,
    "UBER EATS PAYOUT": Category.DELIVERY,
}
