import type { NextConfig } from 'next';
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

const config: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cf.bstatic.com' },
      { protocol: 'https', hostname: '**.bstatic.com' },
    ],
  },
};

export default withNextIntl(config);
