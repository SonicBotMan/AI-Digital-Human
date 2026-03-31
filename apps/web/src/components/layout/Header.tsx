"use client";

import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";

const routeTitles: Record<string, string> = {
  "/knowledge": "Knowledge Graph",
  "/chat": "AI Chat",
  "/admin": "Administration",
  "/api-docs": "API Documentation",
};

export function Header() {
  const pathname = usePathname();
  const title = routeTitles[pathname] ?? "AI Digital Human";

  return (
    <header className="flex h-16 items-center justify-between border-b px-6">
      <div className="flex items-center gap-4">
        <button className="rounded-lg p-2 hover:bg-accent lg:hidden">
          <Menu className="h-5 w-5" />
        </button>
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
          <span className="text-xs font-medium text-primary">U</span>
        </div>
      </div>
    </header>
  );
}
