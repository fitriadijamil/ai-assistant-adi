import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Assistant Adi — CCTV Pre-Sales Tool",
  description: "AI-powered CCTV & Security System Assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-screen bg-base-200">
        <div className="drawer lg:drawer-open">
          <input id="sidebar-drawer" type="checkbox" className="drawer-toggle" />
          <div className="drawer-content flex flex-col">
            <nav className="navbar bg-base-100 lg:hidden shadow-sm px-4">
              <div className="flex-none">
                <label htmlFor="sidebar-drawer" className="btn btn-square btn-ghost">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-5 h-5 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </label>
              </div>
              <div className="flex-1 text-lg font-bold">AI Assistant Adi</div>
            </nav>
            <main className="flex-1">{children}</main>
          </div>
          <div className="drawer-side z-40">
            <label htmlFor="sidebar-drawer" className="drawer-overlay"></label>
            <aside className="menu min-h-full w-64 bg-base-100 p-4 text-base-content border-r border-base-200">
              <div className="mb-6">
                <h2 className="text-xl font-bold">AI Assistant Adi</h2>
                <p className="text-xs text-base-content/50">CCTV Pre-Sales Tool</p>
              </div>
              <ul className="menu">
                <li>
                  <Link href="/" className="flex items-center gap-3">
                    <span className="text-lg">💬</span>
                    Chat Assistant
                  </Link>
                </li>
                <li>
                  <Link href="/proposal-generator" className="flex items-center gap-3">
                    <span className="text-lg">📄</span>
                    Proposal Generator
                  </Link>
                </li>
              </ul>
            </aside>
          </div>
        </div>
      </body>
    </html>
  );
}
