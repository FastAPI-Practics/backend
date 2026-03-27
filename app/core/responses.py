from app.schemas.responses import (
    ForbiddenErrorSchema,
    InternalServerErrorSchema,
    LoginErrorSchema,
    NotFoundErrorSchema,
    OkSchema,
    RegisterErrorSchema,
    UnauthorizedErrorSchema,
)

common_responses = {500: {'model': InternalServerErrorSchema}}

unauthorized_responses = {
    401: {'model': UnauthorizedErrorSchema},
}

auth_responses = {
    **unauthorized_responses,
    403: {'model': ForbiddenErrorSchema},
}

login_responses = {401: {'model': LoginErrorSchema}}

register_responses = {409: {'model': RegisterErrorSchema}}

ok_responses = {200: {'model': OkSchema}}

detail_responses = {404: {'model': NotFoundErrorSchema}}
