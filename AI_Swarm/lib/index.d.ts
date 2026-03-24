import { z } from 'genkit';
export declare const ebookChapterFlow: import("genkit").Action<z.ZodObject<{
    topic: z.ZodString;
    chapterNumber: z.ZodOptional<z.ZodNumber>;
    targetAudience: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    topic: string;
    chapterNumber?: number | undefined;
    targetAudience?: string | undefined;
}, {
    topic: string;
    chapterNumber?: number | undefined;
    targetAudience?: string | undefined;
}>, z.ZodObject<{
    title: z.ZodString;
    introduction: z.ZodString;
    sections: z.ZodArray<z.ZodObject<{
        heading: z.ZodString;
        body: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        heading: string;
        body: string;
    }, {
        heading: string;
        body: string;
    }>, "many">;
    keyTakeaways: z.ZodArray<z.ZodString, "many">;
    closingReflection: z.ZodString;
}, "strip", z.ZodTypeAny, {
    title: string;
    introduction: string;
    sections: {
        heading: string;
        body: string;
    }[];
    keyTakeaways: string[];
    closingReflection: string;
}, {
    title: string;
    introduction: string;
    sections: {
        heading: string;
        body: string;
    }[];
    keyTakeaways: string[];
    closingReflection: string;
}>, z.ZodTypeAny>;
export declare const blogArticleFlow: import("genkit").Action<z.ZodObject<{
    topic: z.ZodString;
    targetKeyword: z.ZodOptional<z.ZodString>;
    targetAudience: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    topic: string;
    targetAudience?: string | undefined;
    targetKeyword?: string | undefined;
}, {
    topic: string;
    targetAudience?: string | undefined;
    targetKeyword?: string | undefined;
}>, z.ZodObject<{
    title: z.ZodString;
    metaDescription: z.ZodString;
    introduction: z.ZodString;
    sections: z.ZodArray<z.ZodObject<{
        heading: z.ZodString;
        body: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        heading: string;
        body: string;
    }, {
        heading: string;
        body: string;
    }>, "many">;
    conclusion: z.ZodString;
    callToAction: z.ZodString;
}, "strip", z.ZodTypeAny, {
    title: string;
    introduction: string;
    sections: {
        heading: string;
        body: string;
    }[];
    metaDescription: string;
    conclusion: string;
    callToAction: string;
}, {
    title: string;
    introduction: string;
    sections: {
        heading: string;
        body: string;
    }[];
    metaDescription: string;
    conclusion: string;
    callToAction: string;
}>, z.ZodTypeAny>;
export declare const emailNewsletterFlow: import("genkit").Action<z.ZodObject<{
    topic: z.ZodString;
    audienceName: z.ZodOptional<z.ZodString>;
    issueNumber: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    topic: string;
    audienceName?: string | undefined;
    issueNumber?: number | undefined;
}, {
    topic: string;
    audienceName?: string | undefined;
    issueNumber?: number | undefined;
}>, z.ZodObject<{
    subjectLine: z.ZodString;
    previewText: z.ZodString;
    greeting: z.ZodString;
    body: z.ZodString;
    callToAction: z.ZodString;
    signOff: z.ZodString;
}, "strip", z.ZodTypeAny, {
    body: string;
    callToAction: string;
    subjectLine: string;
    previewText: string;
    greeting: string;
    signOff: string;
}, {
    body: string;
    callToAction: string;
    subjectLine: string;
    previewText: string;
    greeting: string;
    signOff: string;
}>, z.ZodTypeAny>;
export declare const websiteCopyFlow: import("genkit").Action<z.ZodObject<{
    topic: z.ZodString;
    pageType: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    topic: string;
    pageType?: string | undefined;
}, {
    topic: string;
    pageType?: string | undefined;
}>, z.ZodObject<{
    heroHeadline: z.ZodString;
    heroSubhead: z.ZodString;
    sections: z.ZodArray<z.ZodObject<{
        heading: z.ZodString;
        body: z.ZodString;
        ctaText: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        heading: string;
        body: string;
        ctaText: string;
    }, {
        heading: string;
        body: string;
        ctaText: string;
    }>, "many">;
    socialProofLine: z.ZodString;
    finalCta: z.ZodString;
}, "strip", z.ZodTypeAny, {
    sections: {
        heading: string;
        body: string;
        ctaText: string;
    }[];
    heroHeadline: string;
    heroSubhead: string;
    socialProofLine: string;
    finalCta: string;
}, {
    sections: {
        heading: string;
        body: string;
        ctaText: string;
    }[];
    heroHeadline: string;
    heroSubhead: string;
    socialProofLine: string;
    finalCta: string;
}>, z.ZodTypeAny>;
export declare const xPostFlow: import("genkit").Action<z.ZodObject<{
    topic: z.ZodString;
    style: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    topic: string;
    style?: string | undefined;
}, {
    topic: string;
    style?: string | undefined;
}>, z.ZodObject<{
    post: z.ZodString;
    hashtags: z.ZodArray<z.ZodString, "many">;
    threadFollowUp: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    post: string;
    hashtags: string[];
    threadFollowUp?: string | undefined;
}, {
    post: string;
    hashtags: string[];
    threadFollowUp?: string | undefined;
}>, z.ZodTypeAny>;
export declare const campaignFlow: import("genkit").Action<z.ZodObject<{
    topic: z.ZodString;
    targetAudience: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    topic: string;
    targetAudience?: string | undefined;
}, {
    topic: string;
    targetAudience?: string | undefined;
}>, z.ZodObject<{
    topic: z.ZodString;
    ebook: z.ZodObject<{
        title: z.ZodString;
        introduction: z.ZodString;
        sections: z.ZodArray<z.ZodObject<{
            heading: z.ZodString;
            body: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            heading: string;
            body: string;
        }, {
            heading: string;
            body: string;
        }>, "many">;
        keyTakeaways: z.ZodArray<z.ZodString, "many">;
        closingReflection: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        title: string;
        introduction: string;
        sections: {
            heading: string;
            body: string;
        }[];
        keyTakeaways: string[];
        closingReflection: string;
    }, {
        title: string;
        introduction: string;
        sections: {
            heading: string;
            body: string;
        }[];
        keyTakeaways: string[];
        closingReflection: string;
    }>;
    blog: z.ZodObject<{
        title: z.ZodString;
        metaDescription: z.ZodString;
        introduction: z.ZodString;
        sections: z.ZodArray<z.ZodObject<{
            heading: z.ZodString;
            body: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            heading: string;
            body: string;
        }, {
            heading: string;
            body: string;
        }>, "many">;
        conclusion: z.ZodString;
        callToAction: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        title: string;
        introduction: string;
        sections: {
            heading: string;
            body: string;
        }[];
        metaDescription: string;
        conclusion: string;
        callToAction: string;
    }, {
        title: string;
        introduction: string;
        sections: {
            heading: string;
            body: string;
        }[];
        metaDescription: string;
        conclusion: string;
        callToAction: string;
    }>;
    email: z.ZodObject<{
        subjectLine: z.ZodString;
        previewText: z.ZodString;
        greeting: z.ZodString;
        body: z.ZodString;
        callToAction: z.ZodString;
        signOff: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        body: string;
        callToAction: string;
        subjectLine: string;
        previewText: string;
        greeting: string;
        signOff: string;
    }, {
        body: string;
        callToAction: string;
        subjectLine: string;
        previewText: string;
        greeting: string;
        signOff: string;
    }>;
    website: z.ZodObject<{
        heroHeadline: z.ZodString;
        heroSubhead: z.ZodString;
        sections: z.ZodArray<z.ZodObject<{
            heading: z.ZodString;
            body: z.ZodString;
            ctaText: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            heading: string;
            body: string;
            ctaText: string;
        }, {
            heading: string;
            body: string;
            ctaText: string;
        }>, "many">;
        socialProofLine: z.ZodString;
        finalCta: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        sections: {
            heading: string;
            body: string;
            ctaText: string;
        }[];
        heroHeadline: string;
        heroSubhead: string;
        socialProofLine: string;
        finalCta: string;
    }, {
        sections: {
            heading: string;
            body: string;
            ctaText: string;
        }[];
        heroHeadline: string;
        heroSubhead: string;
        socialProofLine: string;
        finalCta: string;
    }>;
    xPost: z.ZodObject<{
        post: z.ZodString;
        hashtags: z.ZodArray<z.ZodString, "many">;
        threadFollowUp: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        post: string;
        hashtags: string[];
        threadFollowUp?: string | undefined;
    }, {
        post: string;
        hashtags: string[];
        threadFollowUp?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    topic: string;
    ebook: {
        title: string;
        introduction: string;
        sections: {
            heading: string;
            body: string;
        }[];
        keyTakeaways: string[];
        closingReflection: string;
    };
    blog: {
        title: string;
        introduction: string;
        sections: {
            heading: string;
            body: string;
        }[];
        metaDescription: string;
        conclusion: string;
        callToAction: string;
    };
    email: {
        body: string;
        callToAction: string;
        subjectLine: string;
        previewText: string;
        greeting: string;
        signOff: string;
    };
    website: {
        sections: {
            heading: string;
            body: string;
            ctaText: string;
        }[];
        heroHeadline: string;
        heroSubhead: string;
        socialProofLine: string;
        finalCta: string;
    };
    xPost: {
        post: string;
        hashtags: string[];
        threadFollowUp?: string | undefined;
    };
}, {
    topic: string;
    ebook: {
        title: string;
        introduction: string;
        sections: {
            heading: string;
            body: string;
        }[];
        keyTakeaways: string[];
        closingReflection: string;
    };
    blog: {
        title: string;
        introduction: string;
        sections: {
            heading: string;
            body: string;
        }[];
        metaDescription: string;
        conclusion: string;
        callToAction: string;
    };
    email: {
        body: string;
        callToAction: string;
        subjectLine: string;
        previewText: string;
        greeting: string;
        signOff: string;
    };
    website: {
        sections: {
            heading: string;
            body: string;
            ctaText: string;
        }[];
        heroHeadline: string;
        heroSubhead: string;
        socialProofLine: string;
        finalCta: string;
    };
    xPost: {
        post: string;
        hashtags: string[];
        threadFollowUp?: string | undefined;
    };
}>, z.ZodTypeAny>;
export declare const humanizerFlow: import("genkit").Action<z.ZodObject<{
    content: z.ZodString;
    contentType: z.ZodString;
}, "strip", z.ZodTypeAny, {
    content: string;
    contentType: string;
}, {
    content: string;
    contentType: string;
}>, z.ZodObject<{
    humanizedContent: z.ZodString;
    changesApplied: z.ZodArray<z.ZodString, "many">;
}, "strip", z.ZodTypeAny, {
    humanizedContent: string;
    changesApplied: string[];
}, {
    humanizedContent: string;
    changesApplied: string[];
}>, z.ZodTypeAny>;
//# sourceMappingURL=index.d.ts.map