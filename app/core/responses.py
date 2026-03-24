from app.schemas.errors import (
    ForbiddenErrorSchema,
    InternalServerErrorSchema,
    NotFoundErrorSchema,
    UnauthorizedErrorSchema,
)

common_responses = {500: {'model': InternalServerErrorSchema}}

auth_responses = {
    401: {'model': UnauthorizedErrorSchema},
    403: {'model': ForbiddenErrorSchema},
}

detail_responses = {404: {'model': NotFoundErrorSchema}}
