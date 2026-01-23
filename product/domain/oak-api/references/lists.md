# Lists endpoints

## Subjects
- `GET /subjects`
- `GET /subjects/{subject}`
- `GET /subjects/{subject}/sequences`
- `GET /subjects/{subject}/key-stages`
- `GET /subjects/{subject}/years`

## Key stages
- `GET /key-stages`

## Threads
- `GET /threads`
- `GET /threads/{thread}`

## Lessons and units by key stage and subject
- `GET /key-stages/{keyStage}/subject/{subject}/lessons?offset=<n>&limit=<n>`
- `GET /key-stages/{keyStage}/subject/{subject}/units?offset=<n>&limit=<n>`

Notes:
- Lists also include assets by key stage and subject (see doc for exact path).

Source: https://open-api.thenational.academy/docs/api-endpoints/lists
