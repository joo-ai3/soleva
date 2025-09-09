# GitHub Actions Setup Guide

This guide explains how to complete the setup of GitHub Actions workflows for the Soleva platform.

## ✅ Fixed Issues

### 1. Updated Deprecated Actions
- Updated `actions/upload-artifact@v3` to `actions/upload-artifact@v4` ✅
- Updated `actions/cache@v3` to `actions/cache@v4` ✅

### 2. Fixed ESLint Configuration
- Removed `--ext ts,tsx` flag from lint scripts in package.json ✅
- Updated to work with modern eslint.config.js format ✅

### 3. Created Workflow Files
- Created `.github/workflows/frontend.yml` for frontend CI/CD ✅
- Created `.github/workflows/backend.yml` for backend CI/CD ✅
- Created `.github/workflows/notifications.yml` for Slack notifications ✅

## 🔧 Required Setup: Slack Notifications

The notification workflow will automatically detect if the `SLACK_WEBHOOK_URL` secret is configured. If not configured, it will skip sending notifications and log helpful setup instructions.

### Setting up SLACK_WEBHOOK_URL Secret

1. **Create a Slack Webhook URL:**
   - Go to your Slack workspace
   - Navigate to **Apps** > **Incoming Webhooks**
   - Click **Add to Slack**
   - Choose the channel where you want notifications
   - Copy the generated webhook URL

2. **Add the Secret to GitHub Repository:**
   - Go to your GitHub repository
   - Navigate to **Settings** > **Secrets and variables** > **Actions**
   - Click **New repository secret**
   - Name: `SLACK_WEBHOOK_URL`
   - Value: Paste your Slack webhook URL
   - Click **Add secret**

### Webhook URL Format
Your webhook URL should look like:
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

## 📋 Workflow Overview

The GitHub Actions setup includes three separate workflow files:

### Frontend Workflow (`frontend.yml`):
1. **test-frontend** - Lints, type-checks, and builds React frontend
2. **security-scan** - Runs Trivy vulnerability scanner on frontend
3. **build-and-push** - Builds and pushes frontend Docker image

### Backend Workflow (`backend.yml`):
1. **test-backend** - Tests Django backend with PostgreSQL and Redis
2. **security-scan** - Runs Trivy vulnerability scanner on backend  
3. **build-and-push** - Builds and pushes backend Docker image

### Notifications Workflow (`notifications.yml`):
1. **notify** - Sends Slack notifications about workflow completion status
2. Automatically triggered when frontend or backend workflows complete
3. Gracefully handles missing SLACK_WEBHOOK_URL secret

### Triggers:
- **Push** to `main` or `production` branches
- **Pull requests** to `main` branch

## 🔍 Verification

To test the workflows:

1. **Without Slack Setup:**
   - Push a commit to the `main` branch
   - Check the **Actions** tab in your GitHub repository
   - Verify all jobs complete successfully
   - The notification workflow will log that SLACK_WEBHOOK_URL is not configured

2. **With Slack Setup:**
   - Add the `SLACK_WEBHOOK_URL` secret following the instructions above
   - Push another commit to the `main` branch
   - Check your Slack channel for workflow notifications

## 🚀 Additional Secrets (If Needed)

The workflow also references these secrets for production deployment:
- `DEPLOY_HOST` - Production server hostname
- `DEPLOY_USER` - SSH username for deployment
- `DEPLOY_KEY` - SSH private key for deployment

Add these secrets if you plan to use automated deployment to production servers.

## 📝 Notes

- All artifact uploads now use the latest `actions/upload-artifact@v4`
- Cache actions updated to `actions/cache@v4`
- Security reports are uploaded as artifacts for review
- Frontend build artifacts are available for download
- The workflow includes comprehensive testing and security scanning
