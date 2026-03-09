# Nexus - Dummy Authentication Demo

A demonstration Next.js authentication system with secure server-side session management, encrypted cookies, middleware-based route protection, and a beautiful glassmorphic UI.

## 🎯 Features

- **Dummy Authentication** - Simple credential-based login for testing
- **Server-Side Session Management** - Encrypted HTTP-only cookies
- **Route Protection** - Middleware-based protection for authenticated routes
- **Server Components** - RSC for optimal performance and security
- **Modern UI** - Glassmorphic design with dark theme inspired by v0.app
- **No External Dependencies** - No OAuth or external auth services needed
- **TypeScript** - Fully typed for developer experience

## 🏗️ Architecture

### File Structure

```
app/
├── api/auth/
│   ├── login/route.ts           # Login API endpoint
│   └── logout/route.ts          # Logout API endpoint
├── auth/
│   ├── login/page.tsx           # Login page UI
│   └── error/page.tsx           # Error page
├── dashboard/page.tsx           # Protected page
├── repository/page.tsx          # Protected page
├── chat/page.tsx                # Protected page
└── page.tsx                     # Home page

lib/
├── auth.ts                      # Session utilities
├── auth.config.ts               # Auth logic & demo users
└── auth-utils.ts                # Helper functions

components/auth/
├── session-provider.tsx         # Session provider wrapper
└── user-menu.tsx                # User dropdown menu

middleware.ts                    # Route protection
```

### Authentication Flow

```
1. User visits /auth/login → login form
2. Submit email & password → POST /api/auth/login
3. Credentials validated → session created
4. User redirected to /dashboard
5. Middleware checks auth-session cookie
6. Valid session → access protected content
7. Logout → POST /api/auth/logout → redirect to login
```

## 🚀 Getting Started

### 1. Prerequisites

- Node.js 18+
- npm, yarn, or pnpm
- GitHub account

### 2. GitHub OAuth Setup

1. Go to [GitHub Settings → Developer settings → OAuth Apps](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the form:
   - **Application name**: Your app name
   - **Homepage URL**: `http://localhost:3000` (dev) or your domain (prod)
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github` (dev)
4. Copy your **Client ID** and generate a **Client Secret**

### 3. Environment Variables

Create a `.env.local` file with:

```env
# GitHub OAuth
GITHUB_ID=your_github_client_id
GITHUB_SECRET=your_github_client_secret

# Auth Secret (generate with: openssl rand -base64 32)
AUTH_SECRET=your_generated_secret_here

# App URL
AUTH_URL=http://localhost:3000
```

### 4. Install Dependencies

```bash
npm install
# or
pnpm install
```

### 5. Run Development Server

```bash
npm run dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📖 Usage Guide

### Protected Pages

The following routes require authentication:
- `/dashboard` - User dashboard
- `/repository` - Repository browser
- `/chat` - Chat interface

Unauthenticated users are automatically redirected to `/auth/login`.

### Server-Side Auth Check

Use in Server Components to verify authentication:

```typescript
import { requireAuth, getSession } from '@/lib/auth-utils';

export default async function Page() {
  const session = await requireAuth(); // Redirects if not authenticated
  
  return (
    <div>
      <p>Welcome, {session.user?.name}</p>
    </div>
  );
}
```

### Client-Side User Menu

Use the `UserMenu` component to display user info and logout:

```typescript
'use client';

import { useSession } from 'next-auth/react';
import { UserMenu } from '@/components/auth/user-menu';

export default function Header() {
  const { data: session } = useSession();
  return <UserMenu session={session} />;
}
```

### Sign Out

Sign out is handled through the `UserMenu` component, which calls the NextAuth sign-out API.

## 🔒 Security Features

- **Encrypted Sessions** - Session data is encrypted and stored in HTTP-only cookies
- **CSRF Protection** - Built-in CSRF token handling
- **Route Middleware** - Protects routes at the server level
- **No Database Required** - Sessions stored only in encrypted cookies
- **Environment Variable Secrets** - Sensitive data never hardcoded

## 🎨 Design System

The app uses:
- **Color Scheme**: Dark theme with blue accents
- **Typography**: Clean, modern sans-serif
- **Components**: shadcn/ui with custom styling
- **Layout**: Responsive flexbox-based design
- **Effects**: Glassmorphic cards with subtle gradients

## 📱 Pages Overview

### `/` (Home)
Landing page with navigation and overview of protected pages.

### `/auth/login`
Beautiful login page with GitHub OAuth button and feature highlights.

### `/dashboard`
Protected user dashboard showing profile and session info.

### `/repository`
Protected page for browsing and managing repositories.

### `/chat`
Protected chat interface for communication.

### `/auth/error`
Error page for authentication failures.

## 🔧 Customization

### Add New Protected Route

1. Create page in `app/protected-route/page.tsx`
2. Use `requireAuth()` at the top of the component
3. Middleware will automatically protect it

### Customize User Data

Edit `lib/auth.config.ts` callbacks to store additional user data from GitHub:

```typescript
callbacks: {
  async jwt({ token, account, profile }) {
    if (profile) {
      token.customField = profile.customField;
    }
    return token;
  },
}
```

### Update Theme

Modify color tokens in `app/globals.css` to match your brand.

## 🚨 Troubleshooting

### "GITHUB_ID not found"
- Check `.env.local` file exists and has correct variable names
- Restart dev server after adding variables

### "Callback URL doesn't match"
- Verify GitHub OAuth callback URL matches exactly: `http://localhost:3000/api/auth/callback/github`
- For production, update to your domain

### Session not persisting
- Ensure `AUTH_SECRET` is set and valid
- Check cookies are enabled in browser
- Clear browser cookies and try again

## 📚 References

- [Auth.js Documentation](https://authjs.dev/)
- [NextAuth.js v5 Docs](https://next-auth.js.org/)
- [GitHub OAuth Docs](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Next.js Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)

## 📄 License

This project is open source and available under the MIT License.

---

Built with ❤️ using Next.js, Auth.js, and shadcn/ui
