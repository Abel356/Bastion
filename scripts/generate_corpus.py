import json
from pathlib import Path

DEPARTMENTS = {
    "Company": ["Remote Work", "Travel", "Code of Conduct", "Benefits"],
    "Engineering": ["Incident Response", "Deployments", "On Call", "Architecture"],
    "HR": ["Leave", "Hiring", "Performance", "Workplace Safety"],
    "Finance": ["Expenses", "Forecasting", "Compensation", "Procurement"],
    "Security": ["Access Reviews", "Phishing", "Vulnerability Handling", "Data Classification"],
}
CLEARANCE = {"Company": 1, "Engineering": 1, "HR": 2, "Finance": 2, "Security": 3}
INJECTION_INDEXES = {7, 23, 41}


def slug(value: str) -> str:
