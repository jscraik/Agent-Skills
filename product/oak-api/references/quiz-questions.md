# Quiz question endpoints

- `GET /lessons/{lesson}/questions`
- `GET /lessons/{lesson}/questions/exit`
- `GET /lessons/{lesson}/questions/intro`
- `GET /lessons/{lesson}/questions/starter`
- `GET /lessons/{lesson}/questions/lesson`
- `GET /lessons/{lesson}/questions/sequence`

## Filtering by question type
Use the `questionTypes` query parameter. Supported values:
- `short-answer`
- `match`
- `order`
- `multiple-choice`

Example:
- `GET /lessons/{lesson}/questions/exit?questionTypes=short-answer&questionTypes=multiple-choice`

Source: https://open-api.thenational.academy/docs/api-endpoints/quiz-questions
