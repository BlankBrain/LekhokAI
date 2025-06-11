# Google OAuth Setup Instructions for KarigorAI

## 🚀 Quick Setup Guide

### Step 1: Google Cloud Console Setup

1. **Visit Google Cloud Console:**
   - Go to https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create or Select Project:**
   - Create a new project or select existing one
   - Project name: `KarigorAI` (or your preferred name)

3. **Enable APIs:**
   - Go to "APIs & Services" > "Library"
   - Search and enable:
     - Google+ API
     - Google OAuth2 API
     - Google People API (optional, for better profile info)

4. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Choose "Web application"
   - Configure:
     - **Name:** `KarigorAI Web Client`
     - **Authorized JavaScript origins:**
       - `http://localhost:3000` (development)
       - `https://yourdomain.com` (production)
     - **Authorized redirect URIs:**
       - `http://localhost:3000/auth/google/callback` (development)
       - `https://yourdomain.com/auth/google/callback` (production)

5. **Copy Credentials:**
   - Download the JSON file or copy:
     - Client ID
     - Client Secret

### Step 2: Environment Configuration

**Backend (.env in root directory):**
```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_actual_google_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Database Configuration
DATABASE_URL=sqlite:///./karigorai.db

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
SESSION_SECRET=your_session_secret_here

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

**Frontend (ui/.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_actual_google_client_id_here
```

### Step 3: Test the Setup

1. **Start Backend:**
   ```bash
   uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend:**
   ```bash
   cd ui && npm run dev
   ```

3. **Test Google OAuth:**
   - Navigate to `http://localhost:3000/auth`
   - Click "Continue with Google"
   - Should redirect to Google OAuth flow
   - After authorization, should redirect back and complete sign-in

### Step 4: Production Setup

For production deployment:

1. **Update redirect URIs** in Google Cloud Console
2. **Set HTTPS-only** for secure cookies
3. **Update environment variables** with production URLs
4. **Enable secure cookies** in auth routes

## 🔧 Current Implementation Features

### ✅ Working Features:
- **Complete OAuth Flow:** Authorization code exchange
- **User Creation:** Auto-creates users from Google accounts
- **Session Management:** Secure cookie-based sessions
- **Email Registration:** Traditional email/password signup
- **Profile Management:** User profile CRUD operations
- **Organization Support:** Auto-create organizations from signup

### 🚀 Sign-Up Flow Options:

#### Option 1: Google Sign-Up
1. Click "Continue with Google"
2. Redirected to Google OAuth
3. User authorizes KarigorAI
4. Redirected back with authorization code
5. Backend exchanges code for user info
6. User automatically created/logged in
7. Redirected to dashboard

#### Option 2: Email Sign-Up
1. Fill out registration form:
   - Email address
   - Password
   - Username
   - Full name
   - Organization (optional)
   - Accept terms & privacy policy
2. Backend creates user account
3. User automatically logged in
4. Redirected to dashboard

## 📋 TODO for Production:

1. **Email Verification:** Implement email verification for email signups
2. **Password Reset:** Add forgot password functionality
3. **Account Linking:** Allow linking Google account to existing email account
4. **Enhanced Security:** Add 2FA, rate limiting, etc.
5. **User Management:** Admin panel for user approval/management

## 🛠️ Troubleshooting:

### Common Issues:

1. **"Google OAuth not configured"**
   - Check environment variables are set correctly
   - Restart backend server after setting variables

2. **"Invalid redirect URI"**
   - Ensure redirect URI in Google Console matches exactly
   - Check for trailing slashes, http vs https

3. **"Failed to get user information from Google"**
   - Check Google APIs are enabled
   - Verify client credentials are correct

4. **Frontend can't reach backend**
   - Check `NEXT_PUBLIC_API_URL` is set correctly
   - Ensure backend is running on specified port

### Debug Commands:

```bash
# Test backend OAuth endpoint
curl http://localhost:8000/auth/google

# Check environment variables
echo $GOOGLE_CLIENT_ID

# Test backend health
curl http://localhost:8000/system/health
```

## 🔐 Security Notes:

- Never commit `.env` files to version control
- Use different credentials for development/production
- Regularly rotate secrets in production
- Monitor OAuth usage in Google Cloud Console
- Implement proper session timeout and renewal 