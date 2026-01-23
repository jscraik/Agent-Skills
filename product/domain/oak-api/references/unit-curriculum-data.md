# Unit and curriculum data endpoints

## Units
- `GET /units/{unit}`
- `GET /units/{unit}/lessons?offset=<n>&limit=<n>`
- `GET /units/{unit}/optional-lessons`
- `GET /units/{unit}/lesson-choices`

## Key stage + subject
- `GET /key-stages/{keyStage}/subject/{subject}/lessons?offset=<n>&limit=<n>`
- `GET /key-stages/{keyStage}/subject/{subject}/units?offset=<n>&limit=<n>`

## Key stages
- `GET /key-stages`

Notes:
- Unit responses include a lesson list; the lessons endpoint is also available for pagination.

Source: https://open-api.thenational.academy/docs/api-endpoints/unit-and-curriculum-data
