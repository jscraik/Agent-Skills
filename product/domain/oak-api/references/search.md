# Search endpoints

## Endpoints
- `GET /search/lessons`
- `GET /search/units`
- `GET /search/lessons/suggestions`
- `GET /search/units/suggestions`

## Query parameters
- `term` (required for suggestions/results)
- `keyStage`
- `year`
- `subject`
- `sequence`
- `unit`

## Examples
- `/search/lessons/results?term=maths&keyStage=2&subject=maths`
- `/search/units/results?term=maths&keyStage=2&subject=maths`
- `/search/lessons/suggestions?term=math`
- `/search/units/suggestions?term=math`
- `/search/lessons/results?term=math&keyStage=2&year=5&subject=maths&sequence=10`
- `/search/lessons/results?term=math&keyStage=2&year=5&subject=maths&unit=10`

Source: https://open-api.thenational.academy/docs/api-endpoints/search
