"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Check, Copy, Brain, ChevronDown, ChevronRight } from "lucide-react";
import { useState, useCallback, memo } from "react";
import { cn } from "@/lib/utils";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [text]);

  return (
    <button
      onClick={handleCopy}
      className="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-md border border-border/50 bg-muted/80 text-muted-foreground opacity-0 backdrop-blur-sm transition-opacity hover:bg-muted group-hover/code:opacity-100"
      aria-label="Copy code"
    >
      {copied ? (
        <Check className="h-3.5 w-3.5 text-green-500" />
      ) : (
        <Copy className="h-3.5 w-3.5" />
      )}
    </button>
  );
}

// Custom UI Block for `<think>...</think>` transparent reasoning chains.
function ThoughtChainBlock({ content, streaming = false }: { content: string; streaming?: boolean }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="group/thought relative my-4 overflow-hidden rounded-xl border border-primary/20 bg-primary/5 transition-colors hover:border-primary/30">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full select-none items-center justify-between px-4 py-2.5 text-sm font-medium text-primary/80 transition-opacity hover:text-primary"
      >
        <div className="flex items-center gap-2.5">
          <Brain className={cn("h-4 w-4", streaming && "animate-pulse")} />
          <span>{streaming ? "Thinking process..." : "Thought chain"}</span>
        </div>
        <div className="text-primary/50 transition-transform duration-200">
          {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="relative border-t border-primary/10 px-4 py-3 pb-4">
          <div className="text-[0.9em] leading-relaxed text-muted-foreground whitespace-pre-wrap font-mono opacity-90 overflow-x-auto">
            {content}
            {streaming && (
              <span className="ml-1.5 inline-block h-3 w-3 animate-pulse rounded-full bg-primary/60 align-middle shadow-[0_0_8px_rgba(var(--primary),0.5)]" />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const BaseMarkdown = memo(function BaseMarkdown({ content }: { content: string }) {
  // Empty blocks shouldn't collapse the layout
  if (!content) return null;

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          const codeString = String(children).replace(/\n$/, "");

          const isInline =
            !className &&
            !codeString.includes("\n") &&
            node?.position?.start.line === node?.position?.end.line;

          if (!match && isInline) {
            return (
              <code
                className="rounded bg-foreground/10 px-1.5 py-0.5 font-mono text-[0.85em] text-foreground"
                {...props}
              >
                {children}
              </code>
            );
          }

          const language = match?.[1] ?? "text";

          return (
            <div className="group/code relative my-3 overflow-hidden rounded-lg border border-border/50">
              <div className="flex items-center justify-between border-b border-border/50 bg-muted/50 px-4 py-1.5">
                <span className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                  {language}
                </span>
              </div>
              <CopyButton text={codeString} />
              <SyntaxHighlighter
                style={oneDark}
                language={language}
                PreTag="div"
                customStyle={{
                  margin: 0,
                  borderRadius: 0,
                  background: "hsl(var(--muted))",
                  fontSize: "0.8125rem",
                  lineHeight: "1.6",
                  padding: "1rem",
                }}
                codeTagProps={{
                  style: {
                    fontFamily:
                      'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace',
                  },
                }}
              >
                {codeString}
              </SyntaxHighlighter>
            </div>
          );
        },
        p({ children }) {
          return <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>;
        },
        h1({ children }) {
          return <h1 className="mb-3 mt-5 text-xl font-bold first:mt-0">{children}</h1>;
        },
        h2({ children }) {
          return <h2 className="mb-2 mt-4 text-lg font-bold first:mt-0">{children}</h2>;
        },
        h3({ children }) {
          return <h3 className="mb-2 mt-3 text-base font-semibold first:mt-0">{children}</h3>;
        },
        h4({ children }) {
          return <h4 className="mb-1.5 mt-2 text-sm font-semibold first:mt-0">{children}</h4>;
        },
        ul({ children }) {
          return <ul className="mb-3 ml-4 list-disc space-y-1 last:mb-0">{children}</ul>;
        },
        ol({ children }) {
          return <ol className="mb-3 ml-4 list-decimal space-y-1 last:mb-0">{children}</ol>;
        },
        li({ children }) {
          return <li className="leading-relaxed">{children}</li>;
        },
        blockquote({ children }) {
          return (
            <blockquote className="my-3 border-l-2 border-primary/40 pl-4 italic text-muted-foreground">
              {children}
            </blockquote>
          );
        },
        hr() {
          return <hr className="my-4 border-border/50" />;
        },
        a({ href, children }) {
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline decoration-primary/30 underline-offset-2 transition-colors hover:decoration-primary"
            >
              {children}
            </a>
          );
        },
        table({ children }) {
          return (
            <div className="my-3 overflow-x-auto rounded-lg border border-border/50">
              <table className="w-full text-sm">{children}</table>
            </div>
          );
        },
        thead({ children }) {
          return <thead className="bg-muted/50">{children}</thead>;
        },
        th({ children }) {
          return <th className="border-b border-border/50 px-3 py-2 text-left font-semibold">{children}</th>;
        },
        td({ children }) {
          return <td className="border-b border-border/30 px-3 py-2">{children}</td>;
        },
        strong({ children }) {
          return <strong className="font-semibold">{children}</strong>;
        },
        em({ children }) {
          return <em className="italic">{children}</em>;
        },
        pre({ children }) {
          return <>{children}</>;
        },
      }}
    >
      {content}
    </ReactMarkdown>
  );
});

export const MarkdownRenderer = memo(function MarkdownRenderer({
  content,
  className,
}: MarkdownRendererProps) {
  // A simple chunk parser separating DeepSeek-style logic tags <think> from main Markdown
  const blocks: { type: "markdown" | "thought"; content: string; streaming?: boolean }[] = [];
  let currentIndex = 0;

  while (currentIndex < content.length) {
    const thinkStart = content.indexOf("<think>", currentIndex);
    if (thinkStart === -1) {
      blocks.push({ type: "markdown", content: content.slice(currentIndex) });
      break;
    }

    if (thinkStart > currentIndex) {
      blocks.push({ type: "markdown", content: content.slice(currentIndex, thinkStart) });
    }

    const thinkContentStart = thinkStart + 7; // length of <think>
    const thinkEnd = content.indexOf("</think>", thinkContentStart);

    if (thinkEnd === -1) {
      blocks.push({ type: "thought", content: content.slice(thinkContentStart), streaming: true });
      break;
    } else {
      blocks.push({ type: "thought", content: content.slice(thinkContentStart, thinkEnd), streaming: false });
      currentIndex = thinkEnd + 8; // length of </think>
    }
  }

  return (
    <div className={cn("markdown-body", className)}>
      {blocks.map((block, idx) => {
        if (block.type === "thought" && block.content.trim()) {
          return <ThoughtChainBlock key={idx} content={block.content.trim()} streaming={block.streaming} />;
        }
        if (block.type === "markdown" && block.content.trim()) {
          return <BaseMarkdown key={idx} content={block.content} />;
        }
        return null; // Empty blocks
      })}
    </div>
  );
});
