"use client";

import * as React from "react";
import { Cookie } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const CONSENT_KEY = "cookie-consent";

type ConsentValue = "accepted" | "declined";

interface CookieConsentProps {
  /** Override the localStorage key (useful for testing) */
  storageKey?: string;
  /** Additional class names for the outermost wrapper */
  className?: string;
}

/**
 * GDPR cookie consent banner. Persists choice to localStorage.
 * Renders only when no prior consent is stored. Escape key = decline.
 */
function CookieConsent({
  storageKey = CONSENT_KEY,
  className,
}: CookieConsentProps) {
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (!stored) {
        setVisible(true);
      }
    } catch {
      setVisible(true);
    }
  }, [storageKey]);

  const persist = React.useCallback(
    (value: ConsentValue) => {
      try {
        localStorage.setItem(storageKey, value);
      } catch {
        // Storage may be full or blocked — silently ignore
      }
      setVisible(false);
    },
    [storageKey],
  );

  const handleKeyDown = React.useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === "Escape") {
        persist("declined");
      }
    },
    [persist],
  );

  if (!visible) return null;

  return (
    <section
      role="dialog"
      aria-label="Cookie consent"
      aria-description="This website uses cookies to store your preferences, such as theme settings. You can accept or decline non-essential cookies."
      aria-modal="false"
      onKeyDown={handleKeyDown}
      className={cn(
        "fixed inset-x-0 bottom-0 z-50",
        "animate-in slide-in-from-bottom-4 fade-in-0 duration-500",
        "border-t border-border/50 bg-background/80 backdrop-blur-xl",
        "px-4 py-4 sm:px-6 md:py-5",
        className,
      )}
    >
      <div className="mx-auto flex max-w-5xl flex-col gap-4 sm:flex-row sm:items-center sm:gap-6">
        <div className="flex items-start gap-3 sm:items-center sm:flex-1">
          <div
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center",
              "rounded-lg border border-border/60 bg-muted/60",
            )}
            aria-hidden="true"
          >
            <Cookie className="h-5 w-5 text-muted-foreground" />
          </div>
          <div className="space-y-1 text-sm">
            <p className="font-medium leading-snug text-foreground">
              We value your privacy
            </p>
            <p className="text-muted-foreground leading-relaxed">
              We use cookies to remember your preferences (like theme settings)
              and to improve your experience. No marketing or tracking cookies
              are used.
            </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => persist("declined")}
            className="text-muted-foreground"
            aria-label="Decline non-essential cookies"
          >
            Decline
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={() => persist("accepted")}
            aria-label="Accept cookies"
          >
            Accept
          </Button>
        </div>
      </div>
    </section>
  );
}

CookieConsent.displayName = "CookieConsent";

export { CookieConsent };
export type { CookieConsentProps, ConsentValue };
