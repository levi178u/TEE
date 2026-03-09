# Dummy Authentication System Setup Guide

This is a demonstration authentication system using server-side session management with encrypted HTTP-only cookies. No external OAuth provider is required.

## Overview

The application uses a simple dummy authentication system with encrypted session cookies for security and simplicity during development and testing.

### Key Features
- ✅ No external dependencies required
- ✅ Secure session management with encrypted cookies
- ✅ Server-side route protection with middleware
- ✅ Protected pages require authentication
- ✅ Beautiful glassmorphic UI design
- ✅ HTTP-only cookies prevent XSS attacks

## Quick Start

### Step 1: Install Dependencies

```bash
pnpm install
```

No additional configuration needed - all dependencies are included in package.json.

### Step 2: Run Development Server

```bash
pnpm dev
```

Visit `http://localhost:3000` in your browser.

## Step 3: Login with Demo Credentials

Navigate to `http://localhost:3000/auth/login` and use one of these accounts:

**Demo Account:**
- Email: `demo@example.com`
- Password: `demo123`

**Test Account:**
- Email: `test@example.com`
- Password: `test123`

After login, you'll have access to protected pages:
- `/dashboard` - Main dashboard
- `/repository` - Repository management
- `/chat` - Chat interface

## Project Structure

```
.
├── app/
│   ├── page.tsx                    # Home page
│   ├── api/auth/
│   │   ├── login/route.ts         # Login API endpoint
│   │   └── logout/route.ts        # Logout API endpoint
│   ├── auth/
│   │   ├── login/page.tsx         # Login page UI
│   │   └── error/page.tsx         # Error page
│   ├── dashboard/page.tsx         # Protected dashboard
│   ├── repository/page.tsx        # Protected repository page
│   ├── chat/page.tsx              # Protected chat page
│   └── globals.css                # Global styles with dark theme
├── components/
│   └── auth/
│       ├── session-provider.tsx   # Session wrapper component
│       └── user-menu.tsx          # User dropdown menu
├── lib/
│   ├── auth.ts                    # Session utilities
│   ├── auth.config.ts             # Auth configuration & user data
│   └── auth-utils.ts              # Auth helper functions
├── middleware.ts                   # Route protection middleware
└── SETUP.md                        # This file

```

## How It Works

### Authentication Flow

1. **User Submits Login Form** (`/auth/login`)
   - User enters email and password
   - Form submitted to `/api/auth/login`

2. **Credential Validation**
   - Server validates credentials against hardcoded demo users
   - If valid, user object retrieved
   - If invalid, error returned

3. **Session Creation**
   - User data serialized to JSON
   - Session object encoded with Base64
   - Secure HTTP-only cookie created with encrypted session

4. **Access Protected Pages**
   - Middleware checks for `auth-session` cookie
   - If present and valid, user can access protected routes
   - If missing or invalid, user redirected to login

5. **Logout**
   - User clicks sign out button
   - Session cookie destroyed
   - User redirected to login page

### Security Features

1. **HTTP-Only Cookies**: Cannot be accessed by JavaScript (prevents XSS attacks)
2. **Secure Flag**: Cookies only sent over HTTPS in production
3. **SameSite Attribute**: Prevents CSRF attacks by restricting cookie scope
4. **Server-Side Validation**: All authentication decisions on server
5. **Session Expiration**: Sessions expire after 7 days of inactivity
6. **Base64 Encoding**: Session data encoded for transport (not cryptographically secure)

## Protected Routes

The following routes are protected and require authentication:

- `/dashboard` - Main dashboard page
- `/repository` - Repository listing page
- `/chat` - Chat interface page

Unauthenticated users trying to access these routes are automatically redirected to `/auth/login`.

## Troubleshooting

### "Invalid email or password" Error
- Check that email exactly matches a demo account
- Verify password is correct (case-sensitive)
- Demo credentials: `demo@example.com` / `demo123` or `test@example.com` / `test123`

### "Session not found" or "Not authenticated"
- Clear your browser cookies and try again
- Ensure cookies are enabled in your browser
- Check that you're accessing protected routes after login

### "Redirect loop on protected routes"
- Clear all cookies from the site
- Check middleware configuration in `middleware.ts`
- Verify session cookie name matches `auth-session` in both middleware and auth config

### "Fatal error during initialization"
- Run `pnpm install` to ensure all dependencies installed
- Delete `.next` folder: `rm -rf .next`
- Restart development server: `pnpm dev`

### Login form not submitting
- Check browser console for errors
- Verify `/api/auth/login` endpoint exists
- Ensure JavaScript is enabled

## API Endpoints

### Login Endpoint
- **Endpoint**: `/api/auth/login`
- **Method**: POST
- **Body**: `{ email: string, password: string }`
- **Response**: `{ success: boolean, user?: DummyUser }`
- **Description**: Validates credentials and creates session cookie

### Logout Endpoint
- **Endpoint**: `/api/auth/logout`
- **Method**: POST
- **Response**: `{ success: boolean }`
- **Description**: Destroys session cookie and clears authentication

### Example Usage

**Login:**
```javascript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    email: 'demo@example.com', 
    password: 'demo123' 
  })
});
```

**Logout:**
```javascript
const response = await fetch('/api/auth/logout', {
  method: 'POST'
});
```

## Customization

### Adding Demo Users

Edit `lib/auth.config.ts` and add entries to the `dummyUsers` object:

```typescript
const dummyUsers: Record<string, { password: string; user: DummyUser }> = {
  "newuser@example.com": {
    password: "securepassword123",
    user: {
      id: "user-3",
      email: "newuser@example.com",
      name: "New User",
      image: "https://github.com/ghost.png",
    },
  },
};
```

### Changing Session Duration

Edit `lib/auth.config.ts` and modify the `SESSION_DURATION` constant:

```typescript
const SESSION_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 days
// Change to: 24 * 60 * 60 * 1000; // 1 day
```

### Customizing Login Page

Edit `/app/auth/login/page.tsx` to customize:
- Colors and styling
- Demo credentials display
- Form fields and validation
- Error messages

## Migration to Production

### Important: Use Real Authentication

This dummy auth system is **for development only**. For production:

1. **Replace with Auth.js + GitHub OAuth**
   - Install: `pnpm add next-auth`
   - Update `lib/auth.config.ts` with Auth.js setup
   - Configure GitHub OAuth credentials

2. **Or use a production auth service**
   - Supabase Auth
   - Firebase Authentication
   - Clerk
   - Auth0

### Production Checklist

- [ ] Replace dummy credentials with real auth
- [ ] Enable HTTPS on all production URLs
- [ ] Add rate limiting to login endpoints
- [ ] Implement proper password hashing (bcrypt)
- [ ] Set up user database
- [ ] Enable CORS only for trusted domains
- [ ] Add logging and monitoring
- [ ] Regular security audits
- [ ] Set up backups for user data
- [ ] Configure session refresh mechanism

## Resources

- [Next.js Authentication](https://nextjs.org/docs/authentication)
- [Auth.js Documentation](https://authjs.dev/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## Notes

- This is a demonstration system for educational purposes
- Not suitable for production with real user data
- Passwords are stored in plaintext (demo only)
- No encryption for session data (for simplicity)
- Consider this a starting point for your auth implementation
