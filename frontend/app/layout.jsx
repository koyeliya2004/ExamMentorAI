// frontend/app/layout.jsx
// Root layout for ExamMentor AI Next.js app

import "./globals.css";

export const metadata = {
  title: "ExamMentor AI",
  description: "AI-powered exam preparation assistant",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
