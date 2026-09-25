# CBA Catalog API Specification

Version: 4.0

The public API is read-only. Catalog creation and updates are performed with the
authenticated Discovery administration interface or the `import_cba_catalog`
management command.

## Authority by data type

| Data | System of record |
|---|---|
| Course key, organization, number, run, title, pacing | Studio, synchronized to Discovery |
| Course outline and learning content | Studio |
| Catalog descriptions, syllabus, outcomes, references | Discovery |
| Exact duration, price, currency, waitlist status | Discovery |
| Primary and additional catalog categories | Discovery |
| Certificate programs, sequence, requirements, program faculty | Discovery |
| Public catalog presentation | Wagtail consuming this API |
| Organization-code hashes, membership, grants, discounts, permitted products | LMS `orgcode-enterprise` |

Certificate programs are not Studio courses. Their component microcourses are
created in Studio; program metadata and relationships are maintained in Discovery.

## Endpoints

| Endpoint | Status |
|---|---|
| `GET /api/cba/v1/courses/` | Implemented |
| `GET /api/cba/v1/courses/{course_key}/` | Implemented |
| `GET /api/cba/v1/programs/` | Implemented |
| `GET /api/cba/v1/programs/{uuid}/` | Implemented |
| `GET /api/cba/v1/internal/courses/` | Implemented; restricted-catalog permission required |
| `GET /api/cba/v1/internal/courses/{course_key}/` | Implemented; restricted-catalog permission required |
| `GET /api/cba/v1/internal/programs/` | Implemented; restricted-catalog permission required |
| `GET /api/cba/v1/internal/programs/{uuid}/` | Implemented; restricted-catalog permission required |
| `GET /api/cba/v1/organizations/` | Implemented |
| `GET /api/cba/v1/subjects/` | Implemented |
| `GET /api/cba/v1/search/` | Not implemented; returns 501 |
| `GET /api/cba/v1/homepage/` | Not implemented; returns 501 |
| `GET /api/cba/v1/media/` | Not implemented; returns 501 |

## Microcourse response fields

The course-detail endpoint accepts either the native Discovery course key or a
full Studio course-run key such as
`course-v1:CBA+ORF101M01C01+2027`.

| Field | Type | Notes |
|---|---|---|
| `course_key` | string | Full Studio course-run key |
| `organization` | string | Parsed from `course_key` |
| `course_number` | string | Parsed from `course_key` |
| `course_run` | string | Parsed from `course_key` |
| `title` | string | Native course title |
| `pacing` | string | `self_paced` for CBA microcourses |
| `duration_minutes` | integer | Exact expected completion time |
| `price` | decimal string | From the Discovery seat |
| `currency` | string | Three-letter currency code |
| `catalog_status` | string | Includes `waitlist_open` |
| `catalog_visibility` | string | `public` or `hidden` |
| `access_scope` | string | `public`, `organization_code`, or `program_only` |
| `access_policy_key` | string | Non-secret Wagtail policy identifier; never an organization code |
| `standalone_enrollment_allowed` | boolean | False for program-only labs |
| `primary_catalog_category` | string | Canonical active category key |
| `catalog_categories` | array of strings | Active controlled category keys used for filtering |
| `short_description` | HTML string | Native Discovery course field |
| `full_description` | HTML string | Native Discovery course field |
| `learning_outcomes` | array | Structured catalog outcomes |
| `course_overview` | HTML string | Catalog overview |
| `syllabus` | HTML string | Learner-facing instructional outline |
| `references` | array | Standards and other sources |
| `faculty` | array | Zero or more public faculty assignments |
| `course_runs` | array | Native run data plus CBA catalog fields |

The `faculty` array is separate from Studio course-team permissions. Each item
contains the person, public role, credentials, biography, profile information,
and display order.

## Certificate-program response fields

| Field | Type | Notes |
|---|---|---|
| `program_code` | string | Stable CBA program identifier |
| `title` | string | Public certificate title |
| `subtitle` | string | Program subtitle |
| `short_description` | string | Card/search copy |
| `full_description` | HTML string | Detail-page copy |
| `pacing` | string | Program delivery model |
| `duration_minutes` | integer | Total program duration |
| `price` | decimal string | Program price, if sold as a bundle |
| `currency` | string | Three-letter currency code |
| `catalog_status` | string | Includes `waitlist_open` |
| `catalog_visibility` | string | `public` or `hidden` |
| `access_scope` | string | `public` or `organization_code` |
| `access_policy_key` | string | Non-secret Wagtail policy identifier; never an organization code |
| `primary_catalog_category` | string | Canonical active category key |
| `catalog_categories` | array of strings | Active controlled category keys used for filtering |
| `learning_outcomes` | array | Program-level outcomes |
| `course_overview` | HTML string | Program overview |
| `syllabus` | HTML string | Complete program syllabus |
| `completion_requirements` | HTML string | Required learning and award rules |
| `references` | array | Program standards and sources |
| `microcourses` | array | Ordered course-run records with `required` flags |
| `program_faculty` | array | Any number of role-based faculty assignments |

Supported public faculty roles are:

- `program_director`
- `lead_sme`
- `instructor`
- `facilitator`
- `course_author`
- `technical_reviewer`

The same person may hold more than one role. Multiple instructors are supported,
and `display_order` controls the order shown by Wagtail.

## Catalog-category filtering

Course and program collection endpoints accept the optional
`catalog_category` query parameter:

```text
GET /api/cba/v1/courses/?catalog_category=enterprise-risk-management
GET /api/cba/v1/programs/?catalog_category=enterprise-risk-management
GET /api/cba/v1/internal/courses/?catalog_category=enterprise-risk-management
GET /api/cba/v1/internal/programs/?catalog_category=enterprise-risk-management
```

Filtering matches membership in `catalog_categories`. It does not change
visibility or authorization enforcement. Public endpoints still exclude hidden
records. Internal endpoints still require the restricted-catalog permission.
Inactive categories are not returned or matched.

The controlled keys, display labels, bulk-import rules, and Wagtail integration
contract are documented in `docs/api/CATALOG_CATEGORIES.md`.

## Catalog status values

- `draft`
- `waitlist_open`
- `enrollment_open`
- `enrollment_closed`
- `archived`

`waitlist_open` is a CBA catalog state, not a native Studio enrollment state.
While a record is on the waitlist, Studio enrollment should remain closed and
Wagtail should render the **Join Waitlist** call to action.

## Visibility and organization-code enforcement

Anonymous public endpoints return only records whose `catalog_visibility` is
`public`. A hidden course or program returns 404 from its anonymous detail
endpoint. Wagtail uses a dedicated Discovery service account with the
`catalog_extensions.view_restricted_catalog` permission to query `/internal/`.

Discovery never stores or returns an organization code. The LMS
`orgcode-enterprise` application stores only salted code hashes and returns the
signed-in learner's active `access_policy_key`, discount, expiry, and permitted
course/program IDs. Wagtail displays the union of all public products and the
private products explicitly permitted by those grants.

Use these combinations:

| Listing type | `catalog_visibility` | `access_scope` | Policy key | Standalone enrollment |
|---|---|---|---|---|
| Public microcourse/program | `public` | `public` | empty | allowed |
| Org-code microcourse/program | `hidden` | `organization_code` | required | allowed after code validation |
| Certificate-only lab | `hidden` | `program_only` | empty | not allowed |

## Bulk import

Validate a complete JSON file without changing the database:

```bash
python manage.py import_cba_catalog /path/to/catalog.json \
  --partner cba \
  --validate-only
```

Import after the corresponding Studio course shells have synchronized to
Discovery:

```bash
python manage.py import_cba_catalog /path/to/catalog.json \
  --partner cba
```

The import is transactional: validation or database errors roll back the entire
operation. It updates native Discovery descriptions, pacing, syllabus, staff,
program course relationships, and seats, together with the CBA extension fields.

Every microcourse and certificate-program record must include
`primary_catalog_category` and `catalog_categories`. The primary key must also
appear in the category array, and all referenced keys must belong to the active
controlled taxonomy.

The example input is `docs/api/cba_catalog_import.example.json`. The Studio
course-shell loader is `studio-tools/import_cba_studio_courses.py` in the
containing custom-discovery repository.
