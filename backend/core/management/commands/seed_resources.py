from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Category, Resource

CATEGORIES = [
    "Food Assistance",
    "Housing & Shelter",
    "Healthcare",
    "Mental Health",
    "Legal Aid",
    "Employment & Job Training",
    "Financial Assistance",
]

# Sample/placeholder data for local development only — names, addresses and
# phone numbers are fictional, not real organizations.
RESOURCES = [
    # Food Assistance
    {
        "name": "Downtown Community Food Pantry",
        "category": "Food Assistance",
        "zone": "Downtown",
        "address": "120 Market St, Downtown",
        "phone": "(555) 010-1001",
        "hours": "Mon-Fri 9am-4pm",
        "description": "Weekly grocery boxes, no ID required. Walk-ins welcome.",
    },
    {
        "name": "Eastside Family Food Bank",
        "category": "Food Assistance",
        "zone": "Eastside",
        "address": "88 Elm Ave, Eastside",
        "phone": "(555) 010-1002",
        "hours": "Tue & Thu 10am-2pm",
        "description": "Household food distribution, priority for families with children.",
    },
    {
        "name": "Westside Hot Meals Program",
        "category": "Food Assistance",
        "zone": "Westside",
        "address": "45 Cedar Blvd, Westside",
        "phone": "(555) 010-1003",
        "hours": "Daily 12pm-1:30pm",
        "description": "Free hot lunch served daily, no registration needed.",
    },
    # Housing & Shelter
    {
        "name": "North County Emergency Shelter",
        "category": "Housing & Shelter",
        "zone": "North County",
        "address": "300 Birch Rd, North County",
        "phone": "(555) 010-2001",
        "hours": "Open 24/7",
        "description": "Overnight emergency shelter beds for individuals and families.",
    },
    {
        "name": "South County Transitional Housing",
        "category": "Housing & Shelter",
        "zone": "South County",
        "address": "17 Maple Ct, South County",
        "phone": "(555) 010-2002",
        "hours": "Office hours Mon-Fri 8am-5pm",
        "description": "Short-term transitional housing with case management support.",
    },
    {
        "name": "Downtown Rapid Rehousing Office",
        "category": "Housing & Shelter",
        "zone": "Downtown",
        "address": "205 Market St, Downtown",
        "phone": "(555) 010-2003",
        "hours": "Mon-Fri 9am-5pm",
        "description": "Rental assistance and rapid rehousing intake for people facing eviction.",
    },
    # Healthcare
    {
        "name": "Eastside Free Clinic",
        "category": "Healthcare",
        "zone": "Eastside",
        "address": "12 Elm Ave, Eastside",
        "phone": "(555) 010-3001",
        "hours": "Mon, Wed, Fri 8am-3pm",
        "description": "Free primary care and vaccinations, sliding-scale for follow-ups.",
    },
    {
        "name": "Westside Community Health Center",
        "category": "Healthcare",
        "zone": "Westside",
        "address": "60 Cedar Blvd, Westside",
        "phone": "(555) 010-3002",
        "hours": "Mon-Sat 8am-6pm",
        "description": "Primary and urgent care on a sliding-fee scale.",
    },
    {
        "name": "South County Mobile Health Van",
        "category": "Healthcare",
        "zone": "South County",
        "address": "Parked at 17 Maple Ct, South County",
        "phone": "(555) 010-3003",
        "hours": "Wed 10am-2pm",
        "description": "Mobile clinic offering checkups and basic screenings.",
    },
    # Mental Health
    {
        "name": "Downtown Counseling Collective",
        "category": "Mental Health",
        "zone": "Downtown",
        "address": "150 Market St, Downtown",
        "phone": "(555) 010-4001",
        "hours": "Mon-Fri 10am-7pm",
        "description": "Free and low-cost individual counseling, walk-in crisis slots available.",
    },
    {
        "name": "North County Crisis Support Line & Drop-In",
        "category": "Mental Health",
        "zone": "North County",
        "address": "310 Birch Rd, North County",
        "phone": "(555) 010-4002",
        "hours": "Open 24/7 (phone), drop-in Mon-Fri 9am-5pm",
        "description": "24/7 crisis phone support plus daytime drop-in counseling.",
    },
    {
        "name": "Eastside Youth & Family Therapy Center",
        "category": "Mental Health",
        "zone": "Eastside",
        "address": "20 Elm Ave, Eastside",
        "phone": "(555) 010-4003",
        "hours": "Mon-Fri 9am-6pm",
        "description": "Therapy services for children, teens and families on a sliding scale.",
    },
    # Legal Aid
    {
        "name": "Westside Legal Aid Society",
        "category": "Legal Aid",
        "zone": "Westside",
        "address": "75 Cedar Blvd, Westside",
        "phone": "(555) 010-5001",
        "hours": "Mon-Fri 9am-4pm",
        "description": "Free legal help with housing, family and immigration cases.",
    },
    {
        "name": "South County Tenant Rights Clinic",
        "category": "Legal Aid",
        "zone": "South County",
        "address": "22 Maple Ct, South County",
        "phone": "(555) 010-5002",
        "hours": "Thu 1pm-5pm",
        "description": "Free legal clinic focused on eviction defense and tenant rights.",
    },
    {
        "name": "Downtown Immigration Legal Services",
        "category": "Legal Aid",
        "zone": "Downtown",
        "address": "180 Market St, Downtown",
        "phone": "(555) 010-5003",
        "hours": "Mon-Fri 9am-5pm, by appointment",
        "description": "Free consultations on immigration status, asylum and DACA renewals.",
    },
    # Employment & Job Training
    {
        "name": "North County Job Training Center",
        "category": "Employment & Job Training",
        "zone": "North County",
        "address": "330 Birch Rd, North County",
        "phone": "(555) 010-6001",
        "hours": "Mon-Fri 9am-5pm",
        "description": "Resume workshops, job placement assistance and vocational training.",
    },
    {
        "name": "Eastside Career Resource Hub",
        "category": "Employment & Job Training",
        "zone": "Eastside",
        "address": "30 Elm Ave, Eastside",
        "phone": "(555) 010-6002",
        "hours": "Mon-Fri 10am-6pm",
        "description": "Computer lab, job listings and one-on-one career coaching.",
    },
    {
        "name": "Westside Apprenticeship Program",
        "category": "Employment & Job Training",
        "zone": "Westside",
        "address": "90 Cedar Blvd, Westside",
        "phone": "(555) 010-6003",
        "hours": "Mon-Fri 8am-4pm",
        "description": "Paid trade apprenticeships in construction and electrical work.",
    },
    # Financial Assistance
    {
        "name": "Downtown Financial Empowerment Center",
        "category": "Financial Assistance",
        "zone": "Downtown",
        "address": "210 Market St, Downtown",
        "phone": "(555) 010-7001",
        "hours": "Mon-Fri 9am-5pm",
        "description": "Free financial counseling, budgeting help and credit repair guidance.",
    },
    {
        "name": "South County Emergency Utility Fund",
        "category": "Financial Assistance",
        "zone": "South County",
        "address": "25 Maple Ct, South County",
        "phone": "(555) 010-7002",
        "hours": "Mon-Fri 9am-3pm",
        "description": "One-time emergency grants for utility bills and rent arrears.",
    },
]


class Command(BaseCommand):
    help = "Seeds the database with sample categories and resources for local development."

    @transaction.atomic
    def handle(self, *_args, **_options):
        categories = {}
        for name in CATEGORIES:
            category, created = Category.objects.get_or_create(name=name)
            categories[name] = category
            self.stdout.write(
                self.style.SUCCESS(f"Created category: {name}")
                if created
                else f"Category already exists: {name}"
            )

        for data in RESOURCES:
            category_name = data.pop("category")
            resource, created = Resource.objects.get_or_create(
                name=data["name"],
                zone=data["zone"],
                defaults={**data, "category": categories[category_name]},
            )
            data["category"] = category_name
            self.stdout.write(
                self.style.SUCCESS(f"Created resource: {resource.name}")
                if created
                else f"Resource already exists: {resource.name}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {len(CATEGORIES)} categories and {len(RESOURCES)} resources ensured."
            )
        )
