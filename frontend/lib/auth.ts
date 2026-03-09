import { auth as nextAuth } from "./auth.config";

export async function getSession() {
  return await nextAuth();
}

export async function getCurrentUser() {
  const session = await getSession();
  return session?.user;
}
