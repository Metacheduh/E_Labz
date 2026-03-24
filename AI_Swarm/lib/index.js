"use strict";
// ============================================================================
// Jay Shetty-Style AI Content Engine — Powered by Google Genkit
// ============================================================================
// Generates ebooks, blog articles, email newsletters, website copy,
// and X posts about AI workflows & agents in Jay Shetty's voice.
// ============================================================================
Object.defineProperty(exports, "__esModule", { value: true });
exports.humanizerFlow = exports.campaignFlow = exports.xPostFlow = exports.websiteCopyFlow = exports.emailNewsletterFlow = exports.blogArticleFlow = exports.ebookChapterFlow = void 0;
const genkit_1 = require("genkit");
const google_genai_1 = require("@genkit-ai/google-genai");
const express_1 = require("@genkit-ai/express");
// ─── Genkit Initialization ──────────────────────────────────────────────────
const ai = (0, genkit_1.genkit)({
    plugins: [(0, google_genai_1.googleAI)({
            apiKey: process.env.GEMINI_API_KEY || process.env.GOOGLE_GENAI_API_KEY,
        })],
});
const model = google_genai_1.googleAI.model('gemini-2.5-flash');
// ─── Jay Shetty Voice DNA ───────────────────────────────────────────────────
const JAY_SHETTY_SYSTEM = `You are Jay Shetty — bestselling author of "Think Like a Monk," former monk, purpose coach, and storytelling master.

YOUR VOICE DNA:
- Open with personal stories: "I learned in the ashram that..." or "A monk once told me..."
- Bridge ancient wisdom to modern AI concepts naturally
- Use metaphors from nature, meditation, and human growth
- Write with warmth, vulnerability, and quiet confidence
- Make AI feel HUMAN and ACCESSIBLE, not intimidating
- Use the "story → lesson → action" framework
- Reference real tools (Genkit, Google AI, ADK, agent frameworks) as natural discoveries
- Never sound robotic — you're a storyteller first, technologist second
- Use contractions naturally (it's, you're, they've, we're)
- Vary rhythm: short punchy lines. Then flowing, reflective paragraphs.

YOU ARE WRITING ABOUT: AI workflows, AI agents, and Google's AI stack (Genkit, ADK, Vertex AI, Google AI SDK).`;
// ─── Zod Schemas (Structured Output) ────────────────────────────────────────
const EbookSectionSchema = genkit_1.z.object({
    heading: genkit_1.z.string().describe('Section heading'),
    body: genkit_1.z.string().describe('Section body content, 3-5 paragraphs'),
});
const EbookOutputSchema = genkit_1.z.object({
    title: genkit_1.z.string().describe('Compelling chapter title'),
    introduction: genkit_1.z.string().describe('Opening story or reflection, 2-3 paragraphs'),
    sections: genkit_1.z.array(EbookSectionSchema).describe('4-6 content sections'),
    keyTakeaways: genkit_1.z.array(genkit_1.z.string()).describe('3-5 actionable takeaways'),
    closingReflection: genkit_1.z.string().describe('Thoughtful closing that ties back to purpose'),
});
const BlogSectionSchema = genkit_1.z.object({
    heading: genkit_1.z.string(),
    body: genkit_1.z.string(),
});
const BlogOutputSchema = genkit_1.z.object({
    title: genkit_1.z.string().describe('SEO-optimized blog title'),
    metaDescription: genkit_1.z.string().describe('155-char meta description'),
    introduction: genkit_1.z.string().describe('Hook plus context, 2 paragraphs'),
    sections: genkit_1.z.array(BlogSectionSchema).describe('4-5 blog sections with subheadings'),
    conclusion: genkit_1.z.string().describe('Wrap-up paragraph'),
    callToAction: genkit_1.z.string().describe('What the reader should do next'),
});
const EmailOutputSchema = genkit_1.z.object({
    subjectLine: genkit_1.z.string().describe('Curiosity-driven subject line, max 60 chars'),
    previewText: genkit_1.z.string().describe('Inbox preview text, max 90 chars'),
    greeting: genkit_1.z.string().describe('Personal opening greeting'),
    body: genkit_1.z.string().describe('Main newsletter body, 3-5 paragraphs'),
    callToAction: genkit_1.z.string().describe('Clear CTA'),
    signOff: genkit_1.z.string().describe('Warm personal sign-off'),
});
const WebsiteSectionSchema = genkit_1.z.object({
    heading: genkit_1.z.string(),
    body: genkit_1.z.string(),
    ctaText: genkit_1.z.string().describe('CTA button text'),
});
const WebsiteOutputSchema = genkit_1.z.object({
    heroHeadline: genkit_1.z.string().describe('Bold headline, max 10 words'),
    heroSubhead: genkit_1.z.string().describe('Supporting subheadline'),
    sections: genkit_1.z.array(WebsiteSectionSchema).describe('3-4 page sections'),
    socialProofLine: genkit_1.z.string().describe('Social proof or trust signal'),
    finalCta: genkit_1.z.string().describe('Final call-to-action text'),
});
const XPostOutputSchema = genkit_1.z.object({
    post: genkit_1.z.string().describe('Tweet text, max 280 characters'),
    hashtags: genkit_1.z.array(genkit_1.z.string()).describe('2-3 relevant hashtags'),
    threadFollowUp: genkit_1.z.string().optional().describe('Optional follow-up tweet'),
});
const CampaignOutputSchema = genkit_1.z.object({
    topic: genkit_1.z.string(),
    ebook: EbookOutputSchema,
    blog: BlogOutputSchema,
    email: EmailOutputSchema,
    website: WebsiteOutputSchema,
    xPost: XPostOutputSchema,
});
// ─── Content Flows ──────────────────────────────────────────────────────────
// 1. EBOOK CHAPTER FLOW
exports.ebookChapterFlow = ai.defineFlow({
    name: 'ebookChapterFlow',
    inputSchema: genkit_1.z.object({
        topic: genkit_1.z.string().describe('AI workflow/agent topic'),
        chapterNumber: genkit_1.z.number().optional().describe('Chapter number'),
        targetAudience: genkit_1.z.string().optional().describe('Target audience'),
    }),
    outputSchema: EbookOutputSchema,
}, async (input) => {
    const audience = input.targetAudience || 'aspiring developers and entrepreneurs';
    const chapter = input.chapterNumber || 1;
    const { output } = await ai.generate({
        model,
        system: JAY_SHETTY_SYSTEM,
        prompt: `Write chapter ${chapter} of an ebook for ${audience}.

Topic: ${input.topic}

The chapter should have 4-6 sections, each with a heading and rich body content (3-5 paragraphs per section). Include real AI workflow concepts (Genkit flows, agent orchestration, tool use, prompt engineering) woven into storytelling.

Key takeaways must be practical and actionable — things the reader can do TODAY.`,
        output: { schema: EbookOutputSchema },
        config: { temperature: 0.8 },
    });
    if (!output)
        throw new Error('Ebook generation failed.');
    return output;
});
// 2. BLOG ARTICLE FLOW
exports.blogArticleFlow = ai.defineFlow({
    name: 'blogArticleFlow',
    inputSchema: genkit_1.z.object({
        topic: genkit_1.z.string().describe('AI workflow/agent topic'),
        targetKeyword: genkit_1.z.string().optional().describe('Primary SEO keyword'),
        targetAudience: genkit_1.z.string().optional().describe('Target audience'),
    }),
    outputSchema: BlogOutputSchema,
}, async (input) => {
    const audience = input.targetAudience || 'curious creators and builders';
    const seoNote = input.targetKeyword
        ? `\nTarget SEO keyword: "${input.targetKeyword}" — weave it naturally into the title, intro, and headings.`
        : '';
    const { output } = await ai.generate({
        model,
        system: JAY_SHETTY_SYSTEM,
        prompt: `Write a ~1500-word blog article for ${audience}.

Topic: ${input.topic}${seoNote}

Your blog voice:
- Start with a HOOK — a surprising stat, a bold question, or a mini-story
- Write like you're having coffee with a smart friend
- Use short paragraphs and conversational rhythm
- Include specific examples using Google's AI stack (Genkit, ADK, Vertex AI)
- Use subheadings that spark curiosity (questions or bold statements)
- Close with a clear, inspiring call to action

Create 4-5 sections with engaging subheadings. Each section should be 2-3 paragraphs.`,
        output: { schema: BlogOutputSchema },
        config: { temperature: 0.75 },
    });
    if (!output)
        throw new Error('Blog generation failed.');
    return output;
});
// 3. EMAIL NEWSLETTER FLOW
exports.emailNewsletterFlow = ai.defineFlow({
    name: 'emailNewsletterFlow',
    inputSchema: genkit_1.z.object({
        topic: genkit_1.z.string().describe('Newsletter topic'),
        audienceName: genkit_1.z.string().optional().describe('How to address the audience'),
        issueNumber: genkit_1.z.number().optional().describe('Newsletter issue number'),
    }),
    outputSchema: EmailOutputSchema,
}, async (input) => {
    const audience = input.audienceName || 'mindful builders';
    const issueNote = input.issueNumber ? `This is issue #${input.issueNumber}.` : '';
    const { output } = await ai.generate({
        model,
        system: JAY_SHETTY_SYSTEM,
        prompt: `Write a personal email newsletter to your community of ${audience}. ${issueNote}

Topic: ${input.topic}

Your email voice:
- Subject line: create CURIOSITY — make them NEED to open it
- Open like you're writing to ONE person, not a list
- Share a personal reflection or "aha moment" related to the topic
- Keep it intimate — "I've been thinking about..." or "Something happened this week..."
- Teach ONE key insight about AI workflows or agents
- End with a single, clear call to action
- Sign off with warmth — like closing a letter to a friend

Keep it concise (400-600 words). Every sentence should earn its place.`,
        output: { schema: EmailOutputSchema },
        config: { temperature: 0.8 },
    });
    if (!output)
        throw new Error('Email generation failed.');
    return output;
});
// 4. WEBSITE COPY FLOW
exports.websiteCopyFlow = ai.defineFlow({
    name: 'websiteCopyFlow',
    inputSchema: genkit_1.z.object({
        topic: genkit_1.z.string().describe('Page topic'),
        pageType: genkit_1.z.string().optional().describe('landing, about, features, or pricing'),
    }),
    outputSchema: WebsiteOutputSchema,
}, async (input) => {
    const pageType = input.pageType || 'landing';
    const { output } = await ai.generate({
        model,
        system: JAY_SHETTY_SYSTEM,
        prompt: `Write website copy for a ${pageType} page.

Topic: ${input.topic}

Copy principles:
- Hero headline: SHORT, BOLD, PURPOSE-DRIVEN (max 10 words)
- Each section: Empathy → Education → Empowerment
- Use "you" language — speak directly to the visitor
- Make AI feel like a SUPERPOWER, not a threat
- CTAs should be inviting: "Start Your Journey" not "Buy Now"
- Weave in wisdom-driven language: purpose, intention, craft, flow

Create 3-4 sections that guide the visitor from curiosity to action.`,
        output: { schema: WebsiteOutputSchema },
        config: { temperature: 0.7 },
    });
    if (!output)
        throw new Error('Website copy generation failed.');
    return output;
});
// 5. X POST FLOW
exports.xPostFlow = ai.defineFlow({
    name: 'xPostFlow',
    inputSchema: genkit_1.z.object({
        topic: genkit_1.z.string().describe('Topic to tweet about'),
        style: genkit_1.z.string().optional().describe('insight, question, thread-starter, or quote'),
    }),
    outputSchema: XPostOutputSchema,
}, async (input) => {
    const style = input.style || 'insight';
    const { output } = await ai.generate({
        model,
        system: JAY_SHETTY_SYSTEM,
        prompt: `Write an X (Twitter) post. Style: ${style}.

Topic: ${input.topic}

Rules:
- Punchy, quotable, SHAREABLE
- Use the formula: "Most people [common belief]. The truth is [surprising insight]."
- Or: "AI doesn't replace purpose. It amplifies it."
- Mix tech wisdom with life wisdom
- MUST be under 280 characters for the main post
- Include 2-3 relevant hashtags
- Optionally include a thread follow-up that expands with a real example

This should feel like wisdom people screenshot and share.`,
        output: { schema: XPostOutputSchema },
        config: { temperature: 0.9 },
    });
    if (!output)
        throw new Error('X post generation failed.');
    return output;
});
// ─── Campaign Orchestrator Flow ─────────────────────────────────────────────
exports.campaignFlow = ai.defineFlow({
    name: 'campaignFlow',
    inputSchema: genkit_1.z.object({
        topic: genkit_1.z.string().describe('The campaign topic — generates all content types'),
        targetAudience: genkit_1.z.string().optional(),
    }),
    outputSchema: CampaignOutputSchema,
}, async (input) => {
    const { topic, targetAudience } = input;
    const [ebook, blog, email, website, xPost] = await Promise.all([
        (0, exports.ebookChapterFlow)({ topic, targetAudience }),
        (0, exports.blogArticleFlow)({ topic, targetAudience }),
        (0, exports.emailNewsletterFlow)({ topic, audienceName: targetAudience }),
        (0, exports.websiteCopyFlow)({ topic }),
        (0, exports.xPostFlow)({ topic }),
    ]);
    return { topic, ebook, blog, email, website, xPost };
});
// ─── Humanizer Flow ─────────────────────────────────────────────────────────
exports.humanizerFlow = ai.defineFlow({
    name: 'humanizerFlow',
    inputSchema: genkit_1.z.object({
        content: genkit_1.z.string().describe('The AI-generated content to humanize'),
        contentType: genkit_1.z.string().describe('Type: ebook, blog, email, website, xpost'),
    }),
    outputSchema: genkit_1.z.object({
        humanizedContent: genkit_1.z.string().describe('Rewritten, more human-sounding content'),
        changesApplied: genkit_1.z.array(genkit_1.z.string()).describe('What was changed and why'),
    }),
}, async ({ content, contentType }) => {
    const { output } = await ai.generate({
        model,
        prompt: `You are an expert editor who makes AI-generated content sound authentically human.

The following is a ${contentType} written in Jay Shetty's voice about AI workflows and agents.
Make it sound MORE human — remove robotic patterns, add natural imperfections, vary sentence structure.

Rules:
- Keep the Jay Shetty voice and wisdom-driven tone
- Add natural transitions ("Look," "Here's the thing," "And honestly,")
- Vary paragraph lengths — some short, punchy. Some flowing.
- Remove phrases that scream "AI wrote this" (like "In today's rapidly evolving landscape")
- Keep all factual AI/tech content accurate
- Make contractions natural (it's, you're, they've)

Content to humanize:
${content}`,
        output: {
            schema: genkit_1.z.object({
                humanizedContent: genkit_1.z.string(),
                changesApplied: genkit_1.z.array(genkit_1.z.string()),
            }),
        },
        config: { temperature: 0.85 },
    });
    if (!output)
        throw new Error('Humanizer failed.');
    return output;
});
// ─── Express Flow Server ────────────────────────────────────────────────────
(0, express_1.startFlowServer)({
    flows: [
        exports.ebookChapterFlow,
        exports.blogArticleFlow,
        exports.emailNewsletterFlow,
        exports.websiteCopyFlow,
        exports.xPostFlow,
        exports.campaignFlow,
        exports.humanizerFlow,
    ],
    cors: { origin: '*' },
});
//# sourceMappingURL=index.js.map