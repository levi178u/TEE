/*
  Warnings:

  - You are about to drop the column `code` on the `Code` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Code" DROP COLUMN "code";

-- CreateTable
CREATE TABLE "CodeBase" (
    "id" TEXT NOT NULL,
    "language" TEXT NOT NULL,
    "filename" TEXT NOT NULL,
    "route" TEXT NOT NULL,
    "text" TEXT NOT NULL,
    "codeId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "CodeBase_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "CodeBase" ADD CONSTRAINT "CodeBase_codeId_fkey" FOREIGN KEY ("codeId") REFERENCES "Code"("id") ON DELETE CASCADE ON UPDATE CASCADE;
