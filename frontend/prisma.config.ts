import "dotenv/config";
import { defineConfig } from "prisma/config";

export default defineConfig({
  schema: "./prisma/schema.prisma",
  migrations: {
    path: "./prisma/migrations",
  },
  engine: "classic",
  datasource: {
    // Use process.env instead of the non-existent env() function
    url: process.env.DATABASE_URL as string, 
  },
});