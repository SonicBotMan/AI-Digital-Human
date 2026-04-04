import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Shield } from "lucide-react";

export const metadata = {
  title: "Privacy Policy - AI Digital Human",
  description: "Privacy policy for the AI Digital Human platform",
};

const sections = [
  {
    id: "introduction",
    title: "1. Introduction",
    content: `AI Digital Human ("we", "our", or "us") operates the platform accessible at wen.pmparker.net. This Privacy Policy describes how we collect, use, store, and protect your personal information when you use our AI Digital Human platform.

By accessing or using our platform, you agree to the collection and use of information in accordance with this policy. If you do not agree with the terms of this privacy policy, please do not access the platform.`,
  },
  {
    id: "data-collected",
    title: "2. Information We Collect",
    content: null,
    subsections: [
      {
        title: "2.1 Camera Images and Video",
        text: "When you grant camera permissions, we capture image frames for the purpose of AI-driven digital human interaction. These images are processed in real time to generate facial animations and expressions for your digital avatar. Camera data is transmitted to our servers for processing and is not stored beyond the duration necessary for the interaction unless you explicitly save a session.",
      },
      {
        title: "2.2 Microphone Audio",
        text: "When you grant microphone permissions, we capture audio input for speech recognition and voice interaction. Audio data is processed to transcribe your speech and enable real-time conversation with the AI. Audio recordings are not retained after processing unless you explicitly request session recording.",
      },
      {
        title: "2.3 Chat Messages",
        text: "All text messages you send through the chat interface are collected and processed to generate AI responses. Chat history is stored to maintain conversation continuity within your session and to improve the quality of AI interactions.",
      },
      {
        title: "2.4 Knowledge Graph Data",
        text: "The platform constructs and maintains knowledge graphs based on your interactions. This includes entities, relationships, preferences, traits, and other structured data derived from your conversations. Knowledge graph data is used to personalize and improve your AI experience.",
      },
      {
        title: "2.5 Usage and Technical Data",
        text: "We automatically collect certain technical information when you use the platform, including browser type, device information, operating system, IP address, and general usage patterns. This data helps us maintain and improve platform performance and security.",
      },
      {
        title: "2.6 User Preferences",
        text: "We store your preferences regarding theme (light/dark mode), language settings, and other configuration choices to provide a consistent experience across sessions.",
      },
    ],
  },
  {
    id: "how-data-used",
    title: "3. How We Use Your Information",
    content: null,
    items: [
      "Processing real-time camera and audio input to drive AI digital human interactions",
      "Generating AI responses to your chat messages and voice inputs",
      "Building and updating knowledge graphs to personalize your experience",
      "Maintaining conversation history for session continuity",
      "Improving our AI models, algorithms, and platform performance",
      "Detecting and preventing abuse, fraud, or security threats",
      "Providing customer support and responding to your inquiries",
      "Complying with applicable legal obligations",
    ],
  },
  {
    id: "data-sharing",
    title: "4. Data Sharing and Third-Party Services",
    content: `We share certain data with third-party service providers who assist in operating our platform:`,
    subsections: [
      {
        title: "4.1 AI Processing Services",
        text: "Your chat messages, transcribed audio, and processed image data may be transmitted to third-party AI API providers, including GLM (Zhipu AI) and other large language model providers, for the purpose of generating AI responses. These providers process your data under their own privacy and data protection policies.",
      },
      {
        title: "4.2 Service Infrastructure",
        text: "We use cloud infrastructure providers to host and operate the platform. These providers may have access to data as part of their service delivery but are contractually obligated to process data only as instructed by us.",
      },
    ],
    after: `We do not sell your personal data to third parties. We do not share your data for the third parties' own marketing or advertising purposes.`,
  },
  {
    id: "data-retention",
    title: "5. Data Retention and Deletion",
    content: null,
    subsections: [
      {
        title: "5.1 Retention Periods",
        text: "We retain your personal data only for as long as necessary to fulfill the purposes described in this policy. Chat history and knowledge graph data are retained for the duration of your account or session. Camera and audio data are processed in real time and are not stored beyond the immediate processing period unless explicitly requested.",
      },
      {
        title: "5.2 Data Deletion",
        text: "You may request deletion of your personal data at any time by contacting us using the information provided below. Upon receiving a verified deletion request, we will delete your data within a reasonable time frame, except where retention is required by law or for legitimate business purposes such as resolving disputes.",
      },
    ],
  },
  {
    id: "cookies-tracking",
    title: "6. Cookies and Tracking Technologies",
    content: `Our platform uses cookies and similar tracking technologies for the following purposes:

Essential Cookies: Required for the platform to function properly, including session management and authentication.

Preference Cookies: Store your settings such as theme preference (light/dark mode), language selection, and layout preferences.

Analytics Cookies: Help us understand how users interact with the platform by collecting anonymized usage data. These cookies help us improve user experience and platform performance.

You can control cookie preferences through your browser settings. Disabling certain cookies may affect platform functionality. We do not use cookies for cross-site tracking or third-party advertising.`,
  },
  {
    id: "data-security",
    title: "7. Data Security",
    content: `We implement appropriate technical and organizational measures to protect your personal data against unauthorized access, alteration, disclosure, or destruction. These measures include:

Encryption of data in transit using TLS/SSL protocols. Access controls limiting data access to authorized personnel only. Regular security assessments and monitoring of our systems. Secure data storage with appropriate access logging.

While we strive to protect your personal information, no method of transmission over the Internet or electronic storage is completely secure. We cannot guarantee absolute security of your data.`,
  },
  {
    id: "user-rights",
    title: "8. Your Rights",
    content: `Depending on your jurisdiction, you may have the following rights regarding your personal data:`,
    items: [
      "Access: Request a copy of the personal data we hold about you",
      "Correction: Request correction of inaccurate or incomplete personal data",
      "Deletion: Request deletion of your personal data",
      "Portability: Request transfer of your data in a structured, machine-readable format",
      "Restriction: Request restriction of processing of your personal data",
      "Objection: Object to the processing of your personal data in certain circumstances",
      "Withdrawal of Consent: Withdraw consent for data processing where consent is the legal basis",
    ],
    after: `To exercise any of these rights, please contact us using the information provided below. We will respond to your request within a reasonable time frame and in accordance with applicable law.`,
  },
  {
    id: "children",
    title: "9. Children's Privacy",
    content: `Our platform is not directed at children under the age of 13 (or the applicable age of consent in your jurisdiction). We do not knowingly collect personal data from children. If you are a parent or guardian and believe that your child has provided us with personal information, please contact us immediately. We will take steps to delete such information promptly.`,
  },
  {
    id: "policy-updates",
    title: "10. Changes to This Policy",
    content: `We may update this Privacy Policy from time to time to reflect changes in our practices, technologies, legal requirements, or other factors. We will notify you of material changes by posting the updated policy on this page with a revised effective date. We encourage you to review this policy periodically to stay informed about how we protect your information.

Your continued use of the platform after any changes to this policy constitutes your acceptance of the updated terms.`,
  },
  {
    id: "contact",
    title: "11. Contact Us",
    content: `If you have any questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us at:`,
    contactInfo: true,
  },
];

function SectionContent({ content }: { content: string | null }) {
  if (!content) return null;
  return (
    <p className="text-muted-foreground leading-relaxed whitespace-pre-line">
      {content}
    </p>
  );
}

function BulletList({ items }: { items: string[] }) {
  return (
    <ul className="ml-4 mt-4 space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2 text-muted-foreground">
          <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
          <span className="leading-relaxed">{item}</span>
        </li>
      ))}
    </ul>
  );
}

export default function PrivacyPolicyPage() {
  return (
    <div className="container max-w-4xl py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Privacy Policy</h1>
        </div>
        <p className="text-muted-foreground">
          Last updated: April 2, 2026
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          AI Digital Human Platform &mdash; wen.pmparker.net
        </p>
      </div>

      <Card className="mb-8">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Table of Contents</CardTitle>
        </CardHeader>
        <CardContent>
          <nav>
            <ol className="space-y-1.5">
              {sections.map((section) => (
                <li key={section.id}>
                  <a
                    href={`#${section.id}`}
                    className="text-sm text-primary hover:underline transition-colors"
                  >
                    {section.title}
                  </a>
                </li>
              ))}
            </ol>
          </nav>
        </CardContent>
      </Card>

      <div className="space-y-6">
        {sections.map((section) => (
          <Card key={section.id} id={section.id} className="scroll-mt-20">
            <CardHeader>
              <CardTitle className="text-xl">{section.title}</CardTitle>
              {section.content && (
                <CardDescription className="sr-only">
                  Section about {section.title}
                </CardDescription>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              {section.content && (
                <SectionContent content={section.content} />
              )}

              {section.subsections?.map((sub, i) => (
                <div key={i} className="space-y-2">
                  <h4 className="text-sm font-semibold text-foreground">
                    {sub.title}
                  </h4>
                  <p className="text-muted-foreground leading-relaxed">
                    {sub.text}
                  </p>
                </div>
              ))}

              {section.after && (
                <p className="text-muted-foreground leading-relaxed mt-4">
                  {section.after}
                </p>
              )}

              {section.items && <BulletList items={section.items} />}

              {section.contactInfo && (
                <div className="mt-4 rounded-lg border bg-muted/50 p-4 space-y-1.5">
                  <p className="text-sm font-medium text-foreground">
                    AI Digital Human
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Platform:{" "}
                    <a
                      href="https://wen.pmparker.net"
                      className="text-primary hover:underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      wen.pmparker.net
                    </a>
                  </p>
                  <p className="text-sm text-muted-foreground">
                    For privacy inquiries, please reach out through the platform
                    contact form or the email address associated with your
                    account.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-8 text-center text-sm text-muted-foreground border-t pt-6">
        <p>
          This privacy policy applies to the AI Digital Human platform at{" "}
          <a
            href="https://wen.pmparker.net"
            className="text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            wen.pmparker.net
          </a>
          .
        </p>
        <p className="mt-1">
          &copy; {new Date().getFullYear()} AI Digital Human. All rights
          reserved.
        </p>
      </div>
    </div>
  );
}
