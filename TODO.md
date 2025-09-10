# Docker Compose Backend Fix

## Current Issue
- Backend container failing with NameError: name 'sentry_sdk' is not defined
- Error occurs at line 55 in soleva_backend/settings.py during sentry_sdk.init()

## Tasks
- [x] Fix sentry_sdk import issue in settings.py
- [x] Test Docker Compose startup
- [x] Verify backend container health

## Details
The problem is in the Sentry initialization block in settings.py. The sentry_sdk.init() call is outside the try block where sentry_sdk is imported, causing a NameError when the import fails.

## Fix Applied
- Ensured sentry_sdk.init() is properly inside the try-except block
- The import and initialization are now both protected by the same exception handling
