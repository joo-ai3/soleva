# GitHub Actions Setup Guide

This guide explains how to complete the setup of GitHub Actions workflows for the Soleva platform.

## ✅ Fixed Issues

### 1. Updated Deprecated Actions
- Updated `actions/upload-artifact@v3` to `actions/upload-artifact@v4` ✅ (Already completed)
- Updated `actions/cache@v3` to `actions/cache@v4` ✅ (Just completed)

## 🔧 Required Setup: Slack Notifications

The workflow includes Slack notifications for deployment status, but requires a repository secret to be configured.

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

The updated workflow now includes:

### Jobs:
1. **test-backend** - Tests Django backend with PostgreSQL and Redis
2. **test-frontend** - Tests React frontend with linting and type checking
3. **security-scan** - Runs Trivy vulnerability scanner
4. **build-and-push** - Builds and pushes Docker images to GitHub Container Registry
5. **deploy-staging** - Deploys to staging environment (main branch)
6. **deploy-production** - Deploys to production environment (production branch)
7. **notify** - Sends Slack notifications about deployment status

### Triggers:
- **Push** to `main` or `production` branches
- **Pull requests** to `main` branch

## 🔍 Verification

After adding the `SLACK_WEBHOOK_URL` secret:

1. Push a commit to the `main` branch
2. Check the **Actions** tab in your GitHub repository
3. Verify all jobs complete successfully
4. Check your Slack channel for deployment notifications

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
