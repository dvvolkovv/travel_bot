export const metadata = {
  title: 'Hotel Deals Bot',
  description: 'Find the best hotel discounts with an AI chatbot.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
