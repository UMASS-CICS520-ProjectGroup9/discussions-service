# discussions-service

This Django service provides a RESTful API for Discussions and Comments. It is intended to be consumed by the `website-service` frontend, supports simple CRUD operations, and allows filtering comments by discussion ID.

## Features
- List, create, retrieve, update and delete Discussions
- List, create, retrieve, update and delete Comments
- Filter comments by `discussion` id using a query parameter
- Designed for easy integration with frontend templates and API wrappers

## API Endpoints
- `GET /api/discussions/` — List all discussions
- `POST /api/discussions/` — Create a discussion
- `GET /api/discussions/<id>/` — Retrieve discussion
- `PUT /api/discussions/<id>/` — Update discussion
- `DELETE /api/discussions/<id>/` — Delete discussion

- `GET /api/comments/` — List comments (supports filtering by discussion id: `?discussion=<id>`)
- `POST /api/comments/` — Create comment
- `GET /api/comments/<id>/` — Retrieve comment
- `PUT /api/comments/<id>/` — Update comment
- `DELETE /api/comments/<id>/` — Delete comment

Example:
```
GET /api/comments/?discussion=1
```

## Data Model
The important fields are:
- Discussion
  - `id` (AutoField, primary key)
  - `title` (CharField)
  - `body` (TextField)
  - `author` (CharField)
  - `created_at` (DateTimeField)

- Comment
  - `id` (AutoField, primary key)
  - `discussion` (ForeignKey to Discussion)
  - `body` (TextField)
  - `author` (CharField)
  - `created_at` (DateTimeField)
