# CBA Catalog API Specification

Version: 1.0

Implementation Status

| Endpoint | Status |
|----------|--------|
| GET /api/cba/v1/courses/ | ✅ Implemented |
| GET /api/cba/v1/courses/{course_key}/ | ✅ Implemented |
| GET /api/cba/v1/programs/ | 🚧 Planned |
| GET /api/cba/v1/programs/{uuid}/ | 🚧 Planned |
| GET /api/cba/v1/organizations/ | 🚧 Planned |
| GET /api/cba/v1/subjects/ | 🚧 Planned |
| GET /api/cba/v1/search/ | 🚧 Planned |
| GET /api/cba/v1/homepage/ | 🚧 Planned |
| GET /api/cba/v1/media/{id}/ | 🚧 Planned |

Authoritative Service:
Open edX Discovery + catalog_extensions

Base URL

```
/api/cba/v1/
```

---

# Design Principles

- Discovery is the single source of truth.
- CBAUI consumes this API only.
- No catalog business logic exists in CBAUI.
- All endpoints return JSON.
- All list endpoints support pagination.
- All endpoints are read-only.

---

# Endpoints

| Endpoint | Purpose |
|----------|---------|
| GET /courses/ | List courses |
| GET /courses/{course_key}/ | Course detail |
| GET /programs/ | List programs |
| GET /programs/{uuid}/ | Program detail |
| GET /organizations/ | List organizations |
| GET /subjects/ | List subjects |
| GET /homepage/ | Homepage content |
| GET /search/ | Catalog search |
| GET /media/{id}/ | Media metadata |

---

# Course List

GET

```
/api/cba/v1/courses/
```

Response

```json
{
    "count": 0,
    "results": []
}
```

Each course contains

| Field | Type | Required |
|---------|------|----------|
| key | string | Yes |
| uuid | string | Yes |
| title | string | Yes |
| short_description | string | Yes |
| image_url | string | Yes |
| marketing_url | string | Yes |
| organization | object | Yes |
| subjects | array | Yes |

---

# Course Detail

GET

```
/api/cba/v1/courses/{course_key}/
```

Additional fields

- full_description
- course_runs
- instructors
- outcomes
- prerequisites
- syllabus
- seo
- media

---

# Programs

GET

```
/api/cba/v1/programs/
```

Program object

- uuid
- title
- subtitle
- description
- image_url
- banner_url
- organizations
- subjects
- courses
- duration
- level
- marketing_url

---

# Organizations

GET

```
/api/cba/v1/organizations/
```

Returns all organizations.

---

# Subjects

GET

```
/api/cba/v1/subjects/
```

Returns all subjects.

---

# Search

GET

```
/api/cba/v1/search/
```

Supported query parameters

- q
- subject
- organization
- page
- page_size

---

# Homepage

GET

```
/api/cba/v1/homepage/
```

Returns

- hero
- featured_courses
- featured_programs
- featured_subjects
- latest_courses

---

# Media

GET

```
/api/cba/v1/media/{id}/
```

Returns metadata for images and videos.

---

# Architecture

Repository
↓

Service
↓

Serializer
↓

View
↓

REST API
↓

CBAUI
