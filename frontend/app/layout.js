import { Bricolage_Grotesque, Inter } from 'next/font/google';
import './globals.css';

const bricolage = Bricolage_Grotesque({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-bricolage',
});

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata = {
  title: 'VedaAI - AI Assessment Extraction & Answer Mapping',
  description: 'AI-powered question paper and handwritten answer sheet extraction, mapping, and automated grading.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${bricolage.variable} ${inter.variable}`}>
      <body className="bg-gradient-to-b from-[#F5F5F5] to-[#E9E5E5] min-h-screen text-[#2F2F2F] antialiased selection:bg-[#FF5623] selection:text-white">
        {children}
      </body>
    </html>
  );
}
