from app.core.settings import settings

INITIAL_SUBJECTS = ['users', 'pets', 'roles', 'permissions']

INITIAL_ACTIONS = ['detail', 'list', 'create', 'update', 'delete']

INITIAL_PERMISSION_SCHEMA: dict[str, list[str]] = {
    settings.rbac.admin_role: ['*'],
    settings.rbac.public_role: ['users:me'],
    'vet': ['users:me', 'pets:list', 'pets:create'],
}

STANDARD_PERMISSIONS = {
    f'{subject}:{action}': f'{subject.capitalize()} {action}'
    for action in INITIAL_ACTIONS
    for subject in INITIAL_SUBJECTS
}

PERMISSION_DESCRIPTIONS = {
    **STANDARD_PERMISSIONS,
    'users:me': 'Profile view',
}
