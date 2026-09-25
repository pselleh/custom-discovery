# CBA Catalog Categories

Catalog categories provide a controlled taxonomy for filtering microcourses and certificate programs on the Wagtail catalog.

They are presentation and discovery metadata. They do not replace Open edX subjects, organization-code access policies, promotion campaigns, or enrollment permissions.

## API fields

Every imported microcourse and certificate program contains:

| Field | Type | Purpose |
|---|---|---|
| `primary_catalog_category` | string | Main category used for cards, navigation, and canonical grouping |
| `catalog_categories` | array of strings | All categories under which the product may appear |

The primary category must also appear in `catalog_categories`.

Example:

```json
{
  "primary_catalog_category": "enterprise-risk-management",
  "catalog_categories": [
    "enterprise-risk-management",
    "risk-analysis-and-assessment"
  ]
}
```

Only active category keys from the controlled taxonomy are valid. Unknown, inactive, empty, or duplicate category values must be rejected during import validation.

## Controlled taxonomy

| Order | Key | Display name |
|---:|---|---|
| 10 | `organizational-resilience` | Organizational Resilience |
| 20 | `enterprise-risk-management` | Enterprise Risk Management |
| 30 | `risk-analysis-and-assessment` | Risk Analysis and Assessment |
| 40 | `risk-intelligence-and-emerging-risk` | Risk Intelligence and Emerging Risk |
| 50 | `business-continuity-and-crisis-management` | Business Continuity and Crisis Management |
| 60 | `leadership-governance-and-oversight` | Leadership, Governance and Oversight |
| 70 | `audit-assurance-and-forensics` | Audit, Assurance and Forensics |
| 80 | `sector-specific-enterprise-risk-management` | Sector-Specific Enterprise Risk Management |
| 90 | `strategic-environmental-and-threat-analysis` | Strategic, Environmental and Threat Analysis |
| 100 | `quality-and-integrated-management-systems` | Quality and Integrated Management Systems |

## Wagtail filtering

Public catalog requests may filter courses and programs using the `catalog_category` query parameter:

```text
GET /api/cba/v1/courses/?catalog_category=enterprise-risk-management
GET /api/cba/v1/programs/?catalog_category=enterprise-risk-management
```

The authenticated internal endpoints support the same parameter:

```text
GET /api/cba/v1/internal/courses/?catalog_category=enterprise-risk-management
GET /api/cba/v1/internal/programs/?catalog_category=enterprise-risk-management
```

A category filter does not bypass catalog visibility or access controls. Public endpoints continue to exclude hidden products. Internal endpoints continue to require the restricted-catalog permission.

Wagtail should use the category keys returned by Discovery and map them to the approved display labels. Wagtail must not invent new taxonomy keys.

## Bulk-import requirements

Both category fields are required on every microcourse and certificate-program record:

```json
{
  "primary_catalog_category": "organizational-resilience",
  "catalog_categories": [
    "organizational-resilience",
    "business-continuity-and-crisis-management"
  ]
}
```

The importer validates:

1. Both category fields are present.
2. `primary_catalog_category` is a non-empty string.
3. `catalog_categories` is a non-empty array of unique strings.
4. The primary category appears in the category array.
5. Every category key exists.
6. Every referenced category is active.

A successful import replaces the product's existing category relationships with those supplied in the import file.

## Administrative changes

Categories are seeded through the Catalog Extensions migrations and can be reviewed in Django administration.

A category referenced by existing products is protected from accidental deletion. Deactivate obsolete categories instead of deleting them.

## Relationship to access and promotions

Catalog categories describe what subject area a product belongs to.

Access policies determine who may discover or enroll in a product.

Promotion campaigns determine what capacity, date window, or discount applies to an eligible enrollment.

These concerns remain independent. Public and restricted products may use any approved catalog category without changing their access rules.
