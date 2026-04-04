import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import { AuthProvider } from "@/components/layout/AuthProvider";
import { CookieConsent } from "@/components/ui/cookie-consent";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Digital Human",
  description: "Knowledge graph visualization and AI chat platform",
  openGraph: {
    title: "AI Digital Human",
    description: "Knowledge graph visualization and AI chat platform",
    url: "https://wen.pmparker.net",
    type: "website",
    images: [
      {
        url: "https://wen.pmparker.net/og-image.png",
        alt: "AI Digital Human",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Digital Human",
    description: "Knowledge graph visualization and AI chat platform",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          <AuthProvider>
            <AppShell>{children}</AppShell>
            <CookieConsent />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
