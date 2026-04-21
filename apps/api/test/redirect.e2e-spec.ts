import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import request from 'supertest';
import { AppModule } from '../src/app.module';
import { PrismaService } from '../src/prisma/prisma.service';

describe('Redirect endpoint', () => {
  let app: INestApplication;
  let prisma: PrismaService;
  const testOfferId = `test-offer-${Date.now()}`;

  beforeAll(async () => {
    const mod: TestingModule = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = mod.createNestApplication();
    await app.init();
    prisma = mod.get(PrismaService);

    await prisma.offerSnapshot.create({
      data: {
        id: testOfferId,
        sessionId: 'test-session',
        source: 'booking.com',
        hotelId: testOfferId,
        hotelName: 'Test Hotel',
        checkin: new Date('2026-06-10'),
        checkout: new Date('2026-06-15'),
        guests: 2,
        priceUsd: 100 as any,
        priceOrig: { amount: 100, currency: 'USD' } as any,
        bookingUrl: 'https://www.booking.com/hotel/test.html',
        rawJson: {} as any,
      },
    });
  });

  afterAll(async () => {
    await prisma.clickLog.deleteMany({ where: { offerId: testOfferId } });
    await prisma.offerSnapshot.delete({ where: { id: testOfferId } });
    await app.close();
  });

  it('GET /r/<id> logs click and redirects 302 to Booking', async () => {
    const r = await request(app.getHttpServer()).get(`/r/${testOfferId}`);
    expect(r.status).toBe(302);
    expect(r.headers.location).toContain('booking.com');

    const logs = await prisma.clickLog.findMany({ where: { offerId: testOfferId } });
    expect(logs.length).toBe(1);
  });

  it('GET /r/<unknown> returns 404', async () => {
    const r = await request(app.getHttpServer()).get('/r/nonexistent');
    expect(r.status).toBe(404);
  });
});
