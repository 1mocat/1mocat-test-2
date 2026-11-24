#!/usr/bin/env python3
"""JSON processor to transform CSV data into organization.json per schema."""

import csv
import json
import datetime
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = Path(__file__).parent / "organization.json"

def main():
    depts = {}
    with open(DATA_DIR / "departments.csv") as f:
        for row in csv.DictReader(f):
            depts[row["id"]] = {
                "id": row["id"],
                "name": row["name"],
                "budget": float(row["budget"]),
                "employees": [],
                "projects": []
            }

    employees = []
    with open(DATA_DIR / "employees.csv") as f:
        for row in csv.DictReader(f):
            emp = {
                "id": row["id"],
                "name": row["name"],
                "position": row["position"],
                "skills": [s.strip() for s in row["skills"].split(";") if s.strip()],
                "years_of_service": int(row["years_of_service"])
            }
            depts[row["department_id"]]["employees"].append(emp)
            employees.append(emp)

    with open(DATA_DIR / "projects.csv") as f:
        for row in csv.DictReader(f):
            proj = {
                "name": row["name"],
                "status": row["status"],
                "members": [m.strip() for m in row["member_ids"].split(";") if m.strip()],
                "deadline": row["deadline"]
            }
            depts[row["department_id"]]["projects"].append(proj)

    org = {
        "name": "Global Tech Organization",
        "founded": "2015-01-01",
        "departments": list(depts.values())
    }

    budgets = [d["budget"] for d in depts.values()]
    avg_budget = sum(budgets) / len(budgets) if budgets else 0
    total_emp = len(employees)
    skill_dist = Counter()
    for e in employees:
        for s in e["skills"]:
            skill_dist[s] += 1
    dept_sizes = {d["name"]: len(d["employees"]) for d in depts.values()}
    status_dist = Counter()
    for d in depts.values():
        for p in d["projects"]:
            status_dist[p["status"]] += 1
    avg_years = sum(e["years_of_service"] for e in employees) / total_emp if total_emp else 0

    stats = {
        "averageDepartmentBudget": avg_budget,
        "totalEmployees": total_emp,
        "skillDistribution": dict(skill_dist),
        "departmentSizes": dept_sizes,
        "projectStatusDistribution": dict(status_dist),
        "averageYearsOfService": avg_years
    }

    result = {
        "metadata": {
            "version": "1.0.0",
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generator": "orgjson-processor"
        },
        "organization": org,
        "statistics": stats
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
