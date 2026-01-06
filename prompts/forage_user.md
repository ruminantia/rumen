Please analyze and clean the following scraped web content, transforming it into clean, structured markdown while preserving important information and removing unwanted elements.

**Content to Process:**
{content}

## Processing Requirements

### 1. Content Analysis & Classification

First, analyze the content and identify:
- Content type (news article, blog post, opinion piece, tutorial, etc.)
- Content quality assessment (1-10 score)
- Any error conditions or issues detected
- Main content vs. auxiliary/boilerplate content ratio
- Overall completeness and coherence

### 2. Output Structure

Your output must follow this exact structure:

#### A. YAML Frontmatter

Begin with YAML frontmatter containing metadata:

```yaml
---
title: [Extracted title from content or generated descriptive title]
author: [Extracted author name(s) or "Unknown" if not found]
publication_date: [Extracted date or "Unknown" if not found]
source_url: [Extracted URL or "Not specified"]
content_type: [Article/Blog/News/Opinion/Tutorial/etc.]
quality_score: [1-10 rating based on quality framework]
classification: [Clean/Minor Issues/Major Issues/Blocked/Error]
issues_detected: [List of any issues detected, or "None" if clean]
---
```

#### B. Structured Summary Section

Immediately after the frontmatter, provide a structured summary:

## Content Summary

**Overview**: [2-3 sentence overview of the main topic and purpose]

**Key Points**:
- [First key point or main argument]
- [Second key point or important finding]
- [Third key point or significant detail]
- [Additional key points as needed, typically 3-7 total]

**Quality Assessment**: [1-2 sentences evaluating content quality, completeness, and organization]

**Issues Classification**: [Categorize any issues found or state "No significant issues detected"]

---

#### C. Cleaned Article Body

Provide the full cleaned article with preserved structure and formatting:

## [Main Title of Article]

### [First Major Section]
[Cleaned content with proper markdown formatting]
- Preserved quotes and attributions
- Removed navigation, ads, and unwanted elements
- Maintained logical flow and coherence

### [Second Major Section]
[Continue with cleaned content...]

[Continue for all major sections of the article]

### 3. Error Handling Format

If you encounter error conditions, use this format INSTEAD of the normal structure:

```yaml
---
title: "ERROR: [Error Type]"
author: "N/A"
publication_date: "N/A"
source_url: "Not specified"
content_type: "error_page"
quality_score: 0
classification: "ERROR"
error_type: [ERROR_TYPE_CODE]
error_details: [Detailed description of what was found]
summary: [What happened and why content couldn't be processed]
recommendation: [How to handle or resolve the issue]
issues_detected: ["[Error description]"]
---
```

## Error Types to Detect

### HTTP_404 / Page Not Found
- **Detection**: Content contains "404", "not found", "page removed", "no longer available"
- **Classification**: ERROR with error_type: HTTP_404
- **Output**: Explain the page is unavailable and any details from the error message

### ADDBLOCKER_WARNING
- **Detection**: Content mentions "adblock", "blocked", "whitelist", "disable ad blocker", "please disable"
- **Classification**: ERROR with error_type: ADDBLOCKER_WARNING
- **Output**: Explain content was blocked and suggest whitelisting or disabling adblocker

### BLANK_CONTENT
- **Detection**: Content is <100 characters or >90% boilerplate/navigation
- **Classification**: ERROR with error_type: BLANK_CONTENT
- **Output**: Document that no substantial content was found

### NAVIGATION_ONLY
- **Detection**: Page consists primarily of navigation elements, menus, links with minimal article content
- **Classification**: ERROR with error_type: NAVIGATION_ONLY
- **Output**: Explain this appears to be a directory, listing, or navigation page

### PAYWALL
- **Detection**: Content mentions "subscribe", "premium", "membership required", "create an account to continue"
- **Classification**: ERROR with error_type: PAYWALL
- **Output**: Summarize any available free preview content and note paywall restriction

### ACCESS_RESTRICTED
- **Detection**: Content requires login, registration, or has geographic/access restrictions
- **Classification**: ERROR with error_type: ACCESS_RESTRICTED
- **Output**: Explain access requirement and summarize any visible content

## Content Preservation Guidelines

### MUST Preserve:
- Author names, bylines, and author information
- Publication dates, timestamps, and update information
- Direct quotes, block quotes, and pull quotes with attributions
- Source citations and references
- Headlines and subheadings with proper hierarchy
- Key facts, data, statistics, and evidence
- Main article content and core arguments
- Technical content and code snippets
- Important contextual information

### MUST Remove - Aggressive Cleaning Required:

**Navigation & Links:**
- ALL navigation menus, breadcrumbs, pagination links
- "Read Next", "Recommended for You", "Related Stories", "More from", "You might also like"
- "Read more", "Continue reading", "Full story" links
- Category links, section links, topic tags
- Internal site links to other articles or features
- Comment section links and comment counts

**Advertisements:**
- ALL text containing "Advertisement", "Sponsored", "Promoted Content"
- Text like "Advertisement · Scroll to continue" or "ADVERTISEMENT"
- Ad banners, promotional content blurbs
- Affiliate links and referral URLs

**ALL Images - Remove Completely:**
- Remove ALL image markdown: `
![alt text](url)
`
- Remove image captions like "*Item 1 of 6*"
- Remove image credits and attribution lines
- Remove image URLs with parameters
- Remove "[Image description]" or "(Photo: ...)" text

**Purchase & Subscription Links:**
- "Purchase Licensing", "Purchase Licensing Rights"
- "Subscribe", "Sign up", "Premium access", "Create account"
- "Subscribe now", "Join today", "Become a member"
- Subscription and paywall-related text

**Metadata & Boilerplate:**
- "Reading Time: X minutes" or "Reading Time:** X minutes"
- "Published:", "Updated:", "Authors:" when repeated in body
- "Our Standards:", "Trust Principles", policy links
- Author bio sections at end (unless critical to understanding)

**Social Media:**
- Social share buttons and icons
- Embedded tweets, Facebook posts, Instagram content
- Social media follow links

**Footer & End Matter:**
- Copyright notices (©, "Copyright", "All rights reserved")
- "Terms of Service", "Privacy Policy", "Cookie Policy" links
- Newsletter signup forms
- Site-wide repeated footers
- "End of cleaned article" notices

**Interactive Elements:**
- Polls, quizzes, surveys
- Embedded videos and video players
- Analytics tracking references
- Cookie consent banners

**Specific Text Patterns to Remove:**
- Lines containing only "------" or "=====" separators (unless used as section dividers)
- Multiple blank lines in a row (collapse to single blank line)
- [Purchase Licensing Rights] or [Subscribe] links
- Any URL that goes to licensing, subscription, or site navigation

**Examples of Content to REMOVE:**
```
![People celebrate after the U.S. struck Venezuela...](D37QWXG4AVKC...jpg)
*Item 1 of 6* – A person holds up an image depicting...
[Purchase Licensing Rights](/en/licensereuterscontent/?utm_...)
Advertisement · Scroll to continue
*Reading Time: 3 minutes*
### Read Next
- **56 mins ago** – *Brazil's Bolsonaro awaits court approval...
Our Standards: [The Thomson Reuters Trust Principles](/en/about-us/trust-principles.html)
```

**Examples of Content to KEEP:**
```
> "I'm planning to go back to Venezuela as soon as possible," said Machado
**Maduro**, 63, pleaded not guilty on Monday to narcotics charges
Venezuela has about 303 billion barrels in reserves
Reporting by Reuters bureaux worldwide
```

## CRITICAL REMOVAL CHECKLIST

Before finalizing your output, verify you have removed:
- [ ] ALL image markdown (
![...](...)
)
- [ ] ALL "Advertisement" text
- [ ] ALL "Read Next" or "Related Stories" sections
- [ ] ALL "Purchase Licensing" or subscription links
- [ ] ALL "Reading Time" metadata
- [ ] ALL copyright/footer notices
- [ ] ALL social media embeds
- [ ] ALL author bio sections (unless essential)

If ANY of these elements remain in your output, you have not cleaned aggressively enough.

## Quality Assessment Guidelines

### Score 8-10 (High Quality):
- Complete, well-structured content
- Clear author and publication information
- Minimal unwanted elements (<10% of content)
- Excellent readability and formatting
- Comprehensive coverage of topic
- Coherent and logically organized

### Score 5-7 (Medium Quality):
- Content mostly complete with some gaps
- Some metadata missing or unclear
- Moderate unwanted elements (10-30% of content)
- Generally readable with some formatting issues
- Adequate topic coverage
- Minor organizational problems

### Score 1-4 (Low Quality):
- Significant content missing or incomplete
- Poor structure and formatting
- Excessive unwanted elements (>30% of content)
- Difficult to read or understand
- Incomplete coverage
- Major organizational issues

### Score 0 (Problematic):
- Blocked, 404, or navigation-only
- No substantial article content
- Severely corrupted or inaccessible

## Special Cases

### Multiple Articles on One Page
If the content contains multiple distinct articles:
- Set content_type to "multiple_articles"
- Note in issues_detected: ["Multiple articles combined in single page"]
- Process all articles with clear separators between them
- Include article titles and separators in the cleaned output

### Video-Heavy Content
If content is primarily video-based:
- Set content_type to "video_content"
- Note in issues_detected: ["Page is primarily video-based with minimal text"]
- Extract and organize any available text content, descriptions, or transcripts

### Forum or Social Media
If content is from a forum or social media:
- Set content_type to the appropriate type (forum_post, social_media, etc.)
- Note in issues_detected: ["Content is not a standard article format"]
- Preserve the main post/content and key responses if relevant

## Formatting Requirements

- Use proper markdown syntax throughout (# for headings, etc.)
- Maintain heading hierarchy (H1 for title, H2 for main sections, H3 for subsections)
- Use blockquote format (>) for preserved quotes
- Use code blocks for any technical content
- Include blank lines between sections for readability
- Use bullet points for lists and key information
- Preserve emphasis (bold/italic) where it adds clarity

## Final Output Requirements

Your output should:
1. Begin with YAML frontmatter containing all required metadata
2. Include a structured summary section with overview, key points, and quality assessment
3. Provide the full cleaned article body with proper formatting
4. Be well-structured, readable, and ready for downstream processing
5. Accurately classify any errors with detailed explanations when present

Focus on transforming the noisy scraped content into clean, valuable, well-structured information that preserves what matters while removing what doesn't.
