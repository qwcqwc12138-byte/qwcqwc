import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { headers } from "next/headers";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host") ?? "localhost:3000";
  const protocol = requestHeaders.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");
  const baseUrl = new URL(`${protocol}://${host}`);
  const socialImage = new URL("/og.png", baseUrl).toString();

  return {
    metadataBase: baseUrl,
    title: "Market Portfolio Lab | Reproducible Portfolio Research",
    description: "An English-language research site for reproducible stock data analysis, constrained portfolio optimization, and rolling out-of-sample backtests.",
    icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
    openGraph: {
      title: "Market Portfolio Lab",
      description: "15 stocks. 3 sectors. Daily research through September 14, 2026.",
      type: "website",
      images: [{ url: socialImage, width: 1733, height: 909, alt: "Market Portfolio Lab research overview" }],
    },
    twitter: {
      card: "summary_large_image",
      title: "Market Portfolio Lab",
      description: "15 stocks. 3 sectors. Daily research through September 14, 2026.",
      images: [socialImage],
    },
  };
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>{children}</body>
    </html>
  );
}
