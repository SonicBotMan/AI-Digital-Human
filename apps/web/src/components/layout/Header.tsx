"use client";

import { usePathname } from "next/navigation";
import { Menu, Sun, Moon, LogOut, Settings } from "lucide-react";
import { useTheme } from "@/components/layout/ThemeProvider";
import { useAuth } from "@/components/layout/AuthProvider";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const routeTitles: Record<string, string> = {
  "/knowledge": "Knowledge Graph",
  "/chat": "AI Chat",
  "/admin": "Administration",
  "/api-docs": "API Documentation",
  "/terms": "Terms of Service",
  "/privacy": "Privacy Policy",
};

interface HeaderProps {
  onToggleSidebar: () => void;
}

export function Header({ onToggleSidebar }: HeaderProps) {
  const pathname = usePathname();
  const title = routeTitles[pathname] ?? "AI Digital Human";
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  return (
    <header className="flex h-16 items-center justify-between border-b px-6">
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="rounded-lg p-2 hover:bg-accent lg:hidden"
          aria-label="Toggle sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
        >
          {theme === "light" ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </Button>
        {user && (
          <>
            <div className="flex h-8 items-center justify-center rounded-full bg-primary/10 px-3">
              <span className="text-xs font-medium text-primary">
                {user.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <Link href="/settings">
              <Button variant="ghost" size="icon" aria-label="Settings">
                <Settings className="h-5 w-5" />
              </Button>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              onClick={logout}
              aria-label="Sign out"
            >
              <LogOut className="h-5 w-5" />
            </Button>
          </>
        )}
      </div>
    </header>
  );
}
