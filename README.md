# inc-cg-reporter

1. `poetry shell`
2. `poetry install`


* `sls deploy`
* `AWS_CLIENT_TIMEOUT=900000 sls invoke -f generate_report`

Curl:

Note that batch size is capped at 100

* `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/field_data' | jq .`
* `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/field_definitions?per_page=100' | jq . > field_definitions_cg.json`
* All field data: `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/field_data' | jq .`
* Specific field data: `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/field_data/9378477?include=field_definition' | jq .`
* Person by ID: `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/people?where%5Bid%5D=2462759' | jq . > person.json`
* Person by ID: `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET https://api.planningcenteronline.com/people/v2/people/2373585 | jq .`
* Person by single criteria: `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/people/?where%5Bfirst_name%5D=John' |jq .`
* Person by multiple criteria: `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/people/?where%5Bfirst_name%5D=John&where%5Blast_name%5D=Smith' |jq .`
* Peron by multiple criteria with full data: `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/people/?where%5Bfirst_name%5D=John&where%5Blast_name%5D=Smith&include=field_data' |jq .`
* (Water Baptism Date custom field): `curl -H 'Accept: application/vnd.api+json' -u $PC_APPLICATION_ID:$PC_SECRET 'https://api.planningcenteronline.com/people/v2/field_definitions/87410' | jq .`
