import { redirect } from 'next/navigation';
import { auth } from './auth.config';

/**
 * Ensures user is authenticated on the server side.
 * Redirects to login if no session exists.
 */
export async function requireAuth() {
  const session = await auth();
  if (!session?.user) {
    redirect('/auth/login');
  }
  return session;
}

/**
 * Safely checks if user is authenticated without redirecting.
 * Use for conditional rendering on protected pages.
 */
export async function checkAuth() {
  return await auth();
}

/**
 * Get the current user from the session.
 */
export async function getCurrentUser() {
  const session = await auth();
  return session?.user || null;
}
