import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "プレミアムトラベル",
  description: "高級温泉旅館の厳選ガイド",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
