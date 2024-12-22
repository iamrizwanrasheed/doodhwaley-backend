import os
from pathlib import Path

# Update ALLOWED_HOSTS
ALLOWED_HOSTS = ['127.0.0.1', '.vercel.app', 'localhost']

# Add this for static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Add WhiteNoise middleware
MIDDLEWARE = [
    # ...
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]

# Configure WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' 