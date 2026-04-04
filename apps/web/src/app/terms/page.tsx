"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { ScrollText } from "lucide-react";

const LAST_UPDATED = "April 2, 2026";

interface TermSection {
  id: string;
  title: string;
  content: React.ReactNode;
}

const sections: TermSection[] = [
  {
    id: "acceptance",
    title: "1. Acceptance of Terms",
    content: (
      <>
        <p>
          By accessing or using the AI Digital Human platform (&quot;Service&quot;),
          available at{" "}
          <a
            href="https://wen.pmparker.net"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline underline-offset-4 hover:text-primary/80"
          >
            wen.pmparker.net
          </a>
          , you agree to be bound by these Terms of Service (&quot;Terms&quot;).
          If you do not agree to all of these Terms, you may not access or use
          the Service.
        </p>
        <p>
          These Terms constitute a legally binding agreement between you and the
          platform operator. We reserve the right to update these Terms at any
          time as described below.
        </p>
      </>
    ),
  },
  {
    id: "description",
    title: "2. Description of Service",
    content: (
      <>
        <p>
          The AI Digital Human platform provides an interactive artificial
          intelligence experience that combines:
        </p>
        <ul className="my-3 ml-6 list-disc space-y-1.5">
          <li>
            <strong>AI Chat</strong> &mdash; Real-time conversational AI
            interactions powered by large language models.
          </li>
          <li>
            <strong>Knowledge Graphs</strong> &mdash; Visualization and
            management of structured knowledge and entity relationships.
          </li>
          <li>
            <strong>Camera &amp; Vision</strong> &mdash; Camera-based features
            including face detection and visual analysis.
          </li>
          <li>
            <strong>Audio Processing</strong> &mdash; Audio capture and
            processing for voice-based interactions.
          </li>
        </ul>
        <p>
          The Service is provided &quot;as is&quot; and may be modified,
          suspended, or discontinued at any time without prior notice.
        </p>
      </>
    ),
  },
  {
    id: "accounts",
    title: "3. User Accounts &amp; Responsibilities",
    content: (
      <>
        <p>
          Certain features of the Service may require you to create an account.
          When registering, you agree to:
        </p>
        <ul className="my-3 ml-6 list-disc space-y-1.5">
          <li>
            Provide accurate, current, and complete information during
            registration.
          </li>
          <li>
            Maintain and promptly update your account information to keep it
            accurate.
          </li>
          <li>
            Maintain the security and confidentiality of your login credentials.
          </li>
          <li>
            Accept responsibility for all activities that occur under your
            account.
          </li>
          <li>
            Immediately notify us of any unauthorized use of your account.
          </li>
        </ul>
        <p>
          You must not share your account credentials with third parties or use
          another person&apos;s account without authorization.
        </p>
      </>
    ),
  },
  {
    id: "acceptable-use",
    title: "4. Acceptable Use Policy",
    content: (
      <>
        <p>You agree not to use the Service to:</p>
        <ul className="my-3 ml-6 list-disc space-y-1.5">
          <li>
            Violate any applicable local, state, national, or international law
            or regulation.
          </li>
          <li>
            Transmit, store, or promote illegal content, including material that
            is harmful, threatening, abusive, harassing, defamatory, or
            otherwise objectionable.
          </li>
          <li>
            Attempt to gain unauthorized access to any portion of the Service,
            other user accounts, or any systems or networks connected to the
            Service.
          </li>
          <li>
            Use the Service to generate deepfakes, misinformation, or misleading
            content intended to deceive or harm others.
          </li>
          <li>
            Interfere with or disrupt the integrity or performance of the
            Service, including introducing malicious code.
          </li>
          <li>
            Use automated scripts, bots, or scraping tools to access the Service
            without prior written consent.
          </li>
          <li>
            Reverse-engineer, decompile, or disassemble any component of the
            Service.
          </li>
        </ul>
        <p>
          We reserve the right to suspend or terminate access for any user who
          violates this Acceptable Use Policy.
        </p>
      </>
    ),
  },
  {
    id: "ip",
    title: "5. Intellectual Property",
    content: (
      <>
        <p>
          All content, features, and functionality of the Service&mdash;including
          but not limited to text, graphics, logos, icons, images, audio clips,
          software, and their compilation&mdash;are the exclusive property of the
          platform operator or its licensors and are protected by copyright,
          trademark, and other intellectual property laws.
        </p>
        <p>
          You retain ownership of any content you submit to the Service. By
          submitting content, you grant us a limited, non-exclusive, worldwide,
          royalty-free license to use, process, and store that content solely for
          the purpose of providing the Service to you.
        </p>
        <p>
          AI-generated outputs are provided for informational purposes. You
          should not rely on them as original work and should independently
          verify any information provided by the AI.
        </p>
      </>
    ),
  },
  {
    id: "privacy",
    title: "6. Privacy &amp; Data",
    content: (
      <>
        <p>
          The Service processes personal data including chat messages, audio
          input, and camera feeds as necessary to provide the Service. By using
          the Service, you acknowledge that:
        </p>
        <ul className="my-3 ml-6 list-disc space-y-1.5">
          <li>
            Chat interactions may be processed and temporarily stored to provide
            AI responses.
          </li>
          <li>
            Camera and audio data are processed in real-time and are not
            persistently stored unless explicitly configured.
          </li>
          <li>
            Knowledge graph data you create is stored within the platform for
            your use.
          </li>
        </ul>
        <p>
          We implement reasonable security measures to protect your information.
          Your use of the Service is also governed by our privacy practices.
        </p>
      </>
    ),
  },
  {
    id: "warranties",
    title: "7. Disclaimer of Warranties",
    content: (
      <>
        <p>
          THE SERVICE IS PROVIDED ON AN &quot;AS IS&quot; AND &quot;AS
          AVAILABLE&quot; BASIS, WITHOUT ANY WARRANTIES OF ANY KIND, EITHER
          EXPRESS OR IMPLIED.
        </p>
        <p>
          To the fullest extent permitted by applicable law, we disclaim all
          warranties, express or implied, including but not limited to implied
          warranties of merchantability, fitness for a particular purpose,
          non-infringement, and title.
        </p>
        <p>
          We do not warrant that the Service will be uninterrupted, timely,
          secure, or error-free. AI-generated content may be inaccurate,
          incomplete, or biased. You should not rely solely on AI outputs for
          critical decisions.
        </p>
      </>
    ),
  },
  {
    id: "liability",
    title: "8. Limitation of Liability",
    content: (
      <>
        <p>
          TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL
          THE PLATFORM OPERATOR, ITS AFFILIATES, DIRECTORS, EMPLOYEES, OR
          AGENTS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL,
          OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS,
          DATA, OR OTHER INTANGIBLE LOSSES, RESULTING FROM:
        </p>
        <ul className="my-3 ml-6 list-disc space-y-1.5">
          <li>Your access to or use of (or inability to access or use) the Service.</li>
          <li>
            Any conduct or content of any third party on the Service.
          </li>
          <li>
            Any content obtained from the Service, including AI-generated
            outputs.
          </li>
          <li>
            Unauthorized access, use, or alteration of your transmissions or
            content.
          </li>
        </ul>
      </>
    ),
  },
  {
    id: "indemnification",
    title: "9. Indemnification",
    content: (
      <p>
        You agree to indemnify and hold harmless the platform operator and its
        affiliates, officers, agents, and employees from any claim or demand,
        including reasonable attorneys&apos; fees, made by any third party due to
        or arising out of your use of the Service, your violation of these
        Terms, or your violation of any rights of another person or entity.
      </p>
    ),
  },
  {
    id: "changes",
    title: "10. Changes to Terms",
    content: (
      <>
        <p>
          We reserve the right to modify or replace these Terms at any time at
          our sole discretion. When we make changes, we will:
        </p>
        <ul className="my-3 ml-6 list-disc space-y-1.5">
          <li>Update the &quot;Last Updated&quot; date at the top of this page.</li>
          <li>
            Provide notice through the Service or by other reasonable means.
          </li>
        </ul>
        <p>
          Your continued use of the Service after any such changes constitutes
          acceptance of the new Terms. If you do not agree to the modified Terms,
          you must discontinue use of the Service.
        </p>
      </>
    ),
  },
  {
    id: "governing-law",
    title: "11. Governing Law",
    content: (
      <p>
        These Terms shall be governed by and construed in accordance with the
        laws of the jurisdiction in which the platform operator is established,
        without regard to its conflict of law provisions. Any disputes arising
        from or relating to these Terms or the Service shall be resolved
        exclusively in the competent courts of that jurisdiction.
      </p>
    ),
  },
  {
    id: "contact",
    title: "12. Contact Information",
    content: (
      <>
        <p>
          If you have any questions, concerns, or feedback regarding these Terms
          of Service or the AI Digital Human platform, please contact us at:
        </p>
        <div className="mt-3 rounded-lg bg-muted/50 p-4">
          <p className="font-medium">AI Digital Human Platform</p>
          <p className="mt-1 text-muted-foreground">
            Website:{" "}
            <a
              href="https://wen.pmparker.net"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline underline-offset-4 hover:text-primary/80"
            >
              wen.pmparker.net
            </a>
          </p>
          <p className="text-muted-foreground">
            For general inquiries, please reach out through the platform&apos;s
            contact channels.
          </p>
        </div>
      </>
    ),
  },
];

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6 md:p-8 lg:p-10">
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-muted-foreground">
          <ScrollText className="h-4 w-4" />
          <span className="text-sm">Legal</span>
        </div>
        <h1 className="text-3xl font-bold tracking-tight">
          Terms of Service
        </h1>
        <p className="text-muted-foreground">
          Last updated: {LAST_UPDATED}
        </p>
      </div>

      <Card>
        <CardContent className="p-4">
          <nav>
            <p className="mb-2 text-sm font-medium text-muted-foreground">
              Contents
            </p>
            <ol className="columns-1 gap-x-6 text-sm sm:columns-2">
              {sections.map((s) => (
                <li key={s.id} className="break-inside-avoid">
                  <a
                    href={`#${s.id}`}
                    className="inline-block py-0.5 text-primary underline-offset-4 hover:underline"
                  >
                    {s.title}
                  </a>
                </li>
              ))}
            </ol>
          </nav>
        </CardContent>
      </Card>

      {sections.map((section) => (
        <Card key={section.id} id={section.id} className="scroll-mt-24">
          <CardHeader>
            <CardTitle className="text-xl">{section.title}</CardTitle>
            <CardDescription className="sr-only">
              Section {section.title} of the Terms of Service
            </CardDescription>
          </CardHeader>
          <CardContent className="prose prose-sm max-w-none text-foreground [&_p]:text-muted-foreground [&_strong]:text-foreground">
            {section.content}
          </CardContent>
        </Card>
      ))}

      <div className="border-t pt-6 text-center text-sm text-muted-foreground">
        <p>
          By using the AI Digital Human platform, you acknowledge that you have
          read, understood, and agree to be bound by these Terms of Service.
        </p>
      </div>
    </div>
  );
}
