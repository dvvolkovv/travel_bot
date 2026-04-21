-- CreateTable
CREATE TABLE "chat_session" (
    "id" TEXT NOT NULL,
    "lang" TEXT NOT NULL,
    "currency" TEXT NOT NULL,
    "firstMsgAt" TIMESTAMP(3),
    "lastMsgAt" TIMESTAMP(3),
    "msgCount" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "chat_session_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "offer_snapshot" (
    "id" TEXT NOT NULL,
    "sessionId" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "hotelId" TEXT NOT NULL,
    "hotelName" TEXT NOT NULL,
    "checkin" TIMESTAMP(3) NOT NULL,
    "checkout" TIMESTAMP(3) NOT NULL,
    "guests" INTEGER NOT NULL,
    "priceUsd" DECIMAL(10,2) NOT NULL,
    "priceOrig" JSONB NOT NULL,
    "bookingUrl" TEXT NOT NULL,
    "rawJson" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "offer_snapshot_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "click_log" (
    "id" TEXT NOT NULL,
    "offerId" TEXT NOT NULL,
    "sessionId" TEXT,
    "ip" TEXT,
    "userAgent" TEXT,
    "referer" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "click_log_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "offer_snapshot_sessionId_idx" ON "offer_snapshot"("sessionId");

-- CreateIndex
CREATE INDEX "click_log_offerId_idx" ON "click_log"("offerId");

-- CreateIndex
CREATE INDEX "click_log_createdAt_idx" ON "click_log"("createdAt");
