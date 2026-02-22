# inc-cg-reporter

Generates a monthly Excel report of INC connect group membership from Planning Center Online (PCO), then emails it via SMTP.

## Setup

```bash
poetry install
```

## Configuration

Copy `.env` (already exists, not committed to git) and ensure it contains:

```
PC_APPLICATION_ID=...
PC_SECRET=...
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
EMAIL_FROM=edwin@wordspeak.org
EMAIL_TO=edwin@wordspeak.org
```

The SMTP credentials are for AWS SES (SMTP interface). The PCO credentials are the Planning Center Online app ID and secret.

## Running

```bash
poetry run python -m inc_cg_reporter.app
```

The report is saved as `inc_cg.xlsx` in the current directory and emailed to `EMAIL_TO`.

## Tests

```bash
poetry run pytest
```

## PCO API reference (curl)

Credentials come from `.env` — export them first or substitute inline.

```bash
# All field definitions (capped at 100 per page)
curl -H 'Accept: application/vnd.api+json' \
  -u $PC_APPLICATION_ID:$PC_SECRET \
  'https://api.planningcenteronline.com/people/v2/field_definitions?per_page=100' | jq .

# All field data
curl -H 'Accept: application/vnd.api+json' \
  -u $PC_APPLICATION_ID:$PC_SECRET \
  'https://api.planningcenteronline.com/people/v2/field_data' | jq .

# Specific field data (with definition)
curl -H 'Accept: application/vnd.api+json' \
  -u $PC_APPLICATION_ID:$PC_SECRET \
  'https://api.planningcenteronline.com/people/v2/field_data/9378477?include=field_definition' | jq .

# Person by ID
curl -H 'Accept: application/vnd.api+json' \
  -u $PC_APPLICATION_ID:$PC_SECRET \
  'https://api.planningcenteronline.com/people/v2/people/2373585' | jq .

# Person by name
curl -H 'Accept: application/vnd.api+json' \
  -u $PC_APPLICATION_ID:$PC_SECRET \
  'https://api.planningcenteronline.com/people/v2/people/?where[first_name]=John&where[last_name]=Smith' | jq .

# Person by name with custom field data
curl -H 'Accept: application/vnd.api+json' \
  -u $PC_APPLICATION_ID:$PC_SECRET \
  'https://api.planningcenteronline.com/people/v2/people/?where[first_name]=John&where[last_name]=Smith&include=field_data' | jq .

# Specific field definition (e.g. Water Baptism Date)
curl -H 'Accept: application/vnd.api+json' \
  -u $PC_APPLICATION_ID:$PC_SECRET \
  'https://api.planningcenteronline.com/people/v2/field_definitions/87410' | jq .
```
