import { Controller, Get, Param, Req, Res } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as crypto from 'crypto';
import { Request, Response } from 'express';
import { PrismaService } from '../prisma/prisma.service';

@Controller('r')
export class RedirectController {
  constructor(
    private readonly prisma: PrismaService,
    private readonly config: ConfigService,
  ) {}

  @Get(':offerId')
  async redirect(
    @Param('offerId') offerId: string,
    @Req() req: Request,
    @Res() res: Response,
  ) {
    const snapshot = await this.prisma.offerSnapshot.findUnique({ where: { id: offerId } });
    if (!snapshot) {
      res.status(404).send('Offer not found');
      return;
    }

    await this.prisma.clickLog.create({
      data: {
        offerId,
        sessionId: snapshot.sessionId,
        ip: this.hashIp(req.ip),
        userAgent: req.headers['user-agent']?.slice(0, 500),
        referer: (req.headers.referer as string | undefined)?.slice(0, 500),
      },
    });

    const affiliateId = this.config.get<string>('BOOKING_AFFILIATE_ID');
    const url = affiliateId
      ? this.withAffiliate(snapshot.bookingUrl, affiliateId)
      : snapshot.bookingUrl;

    res.redirect(302, url);
  }

  private hashIp(ip: string | undefined): string | null {
    if (!ip) return null;
    return crypto.createHash('sha256').update(ip).digest('hex').slice(0, 16);
  }

  private withAffiliate(url: string, affiliateId: string): string {
    const sep = url.includes('?') ? '&' : '?';
    return `${url}${sep}aid=${encodeURIComponent(affiliateId)}`;
  }
}
