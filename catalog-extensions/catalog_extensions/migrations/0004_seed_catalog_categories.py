from django.db import migrations


CATEGORIES = (
    {
        "key": "organizational-resilience",
        "name": "Organizational Resilience",
        "description": (
            "Organizational resilience, disruption readiness, "
            "adaptability, and resilience management."
        ),
        "display_order": 10,
    },
    {
        "key": "enterprise-risk-management",
        "name": "Enterprise Risk Management",
        "description": (
            "Enterprise risk governance, risk management frameworks, "
            "risk appetite, controls, and reporting."
        ),
        "display_order": 20,
    },
    {
        "key": "risk-analysis-and-assessment",
        "name": "Risk Analysis and Assessment",
        "description": (
            "Risk identification, analysis, evaluation, assessment "
            "techniques, and decision support."
        ),
        "display_order": 30,
    },
    {
        "key": "risk-intelligence-and-emerging-risk",
        "name": "Risk Intelligence and Emerging Risk",
        "description": (
            "Risk intelligence, emerging-risk detection, indicators, "
            "monitoring, and anticipatory analysis."
        ),
        "display_order": 40,
    },
    {
        "key": "business-continuity-and-crisis-management",
        "name": "Business Continuity and Crisis Management",
        "description": (
            "Business continuity, crisis management, incident response, "
            "recovery, and crisis communication."
        ),
        "display_order": 50,
    },
    {
        "key": "leadership-governance-and-oversight",
        "name": "Leadership, Governance and Oversight",
        "description": (
            "Executive leadership, board and committee governance, "
            "accountability, oversight, and resilience leadership."
        ),
        "display_order": 60,
    },
    {
        "key": "audit-assurance-and-forensics",
        "name": "Audit, Assurance and Forensics",
        "description": (
            "Risk-based auditing, assurance, forensic review, evidence, "
            "investigation, and control evaluation."
        ),
        "display_order": 70,
    },
    {
        "key": "sector-specific-enterprise-risk-management",
        "name": "Sector-Specific Enterprise Risk Management",
        "description": (
            "Enterprise risk management adapted to education, venues, "
            "events, and other specialized operating environments."
        ),
        "display_order": 80,
    },
    {
        "key": "strategic-environmental-and-threat-analysis",
        "name": "Strategic, Environmental and Threat Analysis",
        "description": (
            "Strategic analysis, environmental scanning, threat "
            "assessment, scenario analysis, and horizon scanning."
        ),
        "display_order": 90,
    },
    {
        "key": "quality-and-integrated-management-systems",
        "name": "Quality and Integrated Management Systems",
        "description": (
            "Quality management, integrated management systems, "
            "performance evaluation, and continual improvement."
        ),
        "display_order": 100,
    },
)


def seed_catalog_categories(apps, schema_editor):
    CatalogCategory = apps.get_model(
        "catalog_extensions",
        "CatalogCategory",
    )

    for category in CATEGORIES:
        CatalogCategory.objects.update_or_create(
            key=category["key"],
            defaults={
                "name": category["name"],
                "description": category["description"],
                "display_order": category["display_order"],
                "is_active": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "catalog_extensions",
            "0003_catalog_categories",
        ),
    ]

    operations = [
        migrations.RunPython(
            seed_catalog_categories,
            migrations.RunPython.noop,
        ),
    ]
