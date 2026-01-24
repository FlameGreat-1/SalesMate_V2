import type { Metadata, Viewport } from 'next';
import { Providers } from './providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'SalesMate - Your Intelligent Shopping Assistant',
  description: 'Find the perfect products with AI-powered recommendations',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#000000',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-black text-text-primary antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
