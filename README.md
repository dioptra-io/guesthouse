# guesthouse

[![Tests](https://img.shields.io/github/workflow/status/dioptra-io/guesthouse/Tests?logo=github)](https://github.com/dioptra-io/guesthouse/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/codecov/c/github/dioptra-io/guesthouse?logo=codecov&logoColor=white)](https://app.codecov.io/gh/dioptra-io/guesthouse)

Generate temporary ClickHouse credentials.

```bash
docker compose up
curl -X POST -H 'Content-Type: application/json' -d '{"tables": ["table1"]}' http://localhost:8000
# {
#   "username": "guesthouse_1642969798247293_3d30",
#   "password": "e893960dc3ae5fb58cd95d97771a5b64"
# }
```
