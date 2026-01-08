import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AI Model Studio - Build AI Models Without Code',
  description: 'Transform raw data into production-ready AI models without writing a single line of code.',
  keywords: ['AI', 'Machine Learning', 'No-Code ML', 'AutoML', 'Data Science'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.Node;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
