from app.core.settings import settings

INITIAL_SUBJECTS = ['profile', 'pets', 'roles', 'permissions']

INITIAL_ACTIONS = ['detail', 'list', 'create', 'update', 'delete']

INITIAL_PERMISSION_SCHEMA: dict[str, list[str]] = {
    settings.rbac.admin_role: ['*'],
    settings.rbac.public_role: ['profile:detail'],
    'vet': ['profile:read', 'pets:list', 'pets:create'],
}

PERMISSION_DESCRIPTIONS = {
    'profile:list': 'User list',
    'profile:detail': 'Profile view',
}
