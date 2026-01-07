# Rumen Pipeline Redesign: From Forage to Remasticate

**Date:** 2025-01-07
**Author:** Ber + Claude
**Status:** Design Phase

## Overview

Complete pipeline overhaul to transform raw scraped content into categorized, high-quality news stories through a 5-stage process.

---

## New Pipeline Architecture

```
/app/pastures (raw scraped HTML)
    ↓
[1. FORAGE] Filter/accept-reject based on content tolerances
    ↓
/app/output/forage (approved content with original HTML)
    ↓
[2. GRAZE] Extract into standardized structured markdown format
    ↓
/app/output/graze (structured article data)
    ↓
[3. FERMENT] Classify: Full Story vs Blurb
    ├─→ Full Story → /app/output/ferment/stories (passed to next stage)
    └─→ Blurb → /app/output/ferment/blurbs (stored, not processed further)
    ↓
[4. REGURGITATE] Critique + Research with web search (chew + rehydrate combined)
    ↓
/app/output/regurgitate (researched, critiqued articles)
    ↓
[5. REMASTICATE] Write final polished news story
    ↓
/app/output/remasticate (publication-ready stories)
```

---

## Stage Details

### 1. FORAGE (Unchanged)

**Purpose:** Content filtering gateway
**Input:** `/app/pastures` (raw scraped HTML)
**Output:** `/app/output/forage`
**Decision:** Accept/Reject based on tolerance criteria

**Key Settings:**
- `rejection_trigger_words = DECISION: REJECT`
- `append_input_to_output = false` (changed to avoid token limit issues)

**Prompt:** `forage_system.md` (no changes needed)

---

### 2. GRAZE (Redesigned)

**Purpose:** Extract structured metadata from articles
**Input:** `/app/output/forage` (approved content)
**Output:** `/app/output/graze`
**Function:** Transform into standardized, machine-readable format

**Standardized Output Format:**

```markdown
# Article Title

**Metadata:**
- **URL:** [source URL]
- **Publication Date:** [YYYY-MM-DD]
- **Author:** [author name if available]
- **Source:** [publication/website name]
- **Word Count:** [estimated]
- **Language:** [en/other]
- **Geography:** [countries/regions mentioned]
- **Topics:** [comma-separated tags]
- **Importance Score:** [1-10 scale]

**Summary:**
[2-3 sentence abstract of the article]

**Key Claims:**
1. [First major claim/fact]
   - Source: [attribution if available]
   - Verification Status: [verified/unverified/unclear]

2. [Second major claim/fact]
   - Source: [attribution if available]
   - Verification Status: [verified/unverified/unclear]

**Timeline:**
- [Date/Time]: [Event description]
- [Date/Time]: [Event description]

**Key Entities:**
- **People:** [Person Name] - [Role/Title]
- **Organizations:** [Org Name] - [Description]
- **Locations:** [Location] - [Context]
- **Technologies/Products:** [Name] - [Description]

**Data Points:**
- [Statistic]: [Value]
- [Quantity]: [Amount]
- [Date/Time Range]: [Duration]

**Quotes:**
> "[Notable quote]" — [Attribution], [Context]

**Related Context:**
- [Connection to other events]
- [Background information]

**Content Type Classification:**
- **Primary Type:** [News/Opinion/Analysis/Feature/Interview/etc]
- **Secondary Type:** [Politics/Tech/Science/Business/etc]
- **Format:** [Breaking/Investigative/OpEd/PressRelease/etc]
- **Depth:** [Brief/Standard/In-Depth]

**Actionable Items:**
- [ ] [Claims requiring verification]
- [ ] [Entities requiring further research]
- [ ] [Data points to validate]
```

**Prompt Strategy:**
- Extract ALL available metadata from the article
- Identify key claims, entities, and data points
- Create structured format that's easy for next stages to process
- Score importance based on: novelty, impact, verifiability

---

### 3. FERMENT (New Stage)

**Purpose:** Classify content importance and route appropriately
**Input:** `/app/output/graze` (structured article data)
**Output:**
- Stories: `/app/output/ferment/stories` (passed to regurgitate)
- Blurbs: `/app/output/ferment/blurbs` (stored as-is)

**Decision Criteria:**

**Full Story (passed through) if:**
- Importance Score ≥ 7
- Has verifiable claims requiring investigation
- Contains unique/newsworthy information
- Has sufficient depth (not just a brief update)
- Potential for comprehensive reporting

**Blurb (rephrased and archived) if:**
- Importance Score < 7
- Minor update or brief mention
- Lacks substance for full article
- Routine/ongoing coverage with minimal new info
- Press releases with little news value

**Blurb Format:**
```markdown
## [Publication Name]: [Headline]

**Date:** [YYYY-MM-DD]
**Topics:** [tags]

**Blurb:**
[1-2 sentence summary suitable for quick reading]

**Full Story Potential:** [Why this didn't warrant full coverage]
```

**Rejection (trigger_words):**
- `DECISION: FULL_STORY` → Pass to next stage
- `DECISION: BLURB` → Archive to blurbs folder

**Configuration Requirements:**
- Need `output_directory_blurbs` setting (new feature)
- OR use subdirectory approach within single output_directory

**Implementation Approach:**
Option A: Multiple output directories (requires code changes)
```ini
[ferment]
output_directory_stories = /app/output/ferment/stories
output_directory_blurbs = /app/output/ferment/blurbs
```

Option B: Single directory with filename prefixes (works with current code)
```ini
[ferment]
output_directory = /app/output/ferment
# Stories get normal filenames
# Blurbs get "blurb_" prefix and rejected marker
```

Option C: Use rejection mechanism (easiest with current code)
- Stories: `filename.processed.md` → normal processing
- Blurbs: `filename.blurb.md` → marked and saved, but not processed by next stage

**Recommendation:** Start with Option C (rejection markers) since it works with existing code:
- Full stories: Save as normal `.processed.md`, passed to next stage
- Blurbs: Save as `.blurb.md`, which next stage's `delete_input_files = false` will skip

---

### 4. REGURGITATE (New Combined Stage)

**Purpose:** Critique + Research in one pass
**Input:** `/app/output/ferment/stories` (full stories only)
**Output:** `/app/output/regurgitate`
**Function:**
1. Critique content for gaps, biases, logical issues
2. Use web search to verify claims and gather context
3. Fill in missing information
4. Provide research notes and corrections

**Output Format:**

```markdown
# [Article Title]

## Critique & Analysis

**Strengths:**
- [What the article does well]
- [Reliable sources cited]
- [Good data presentation]

**Weaknesses & Gaps:**
- [Missing context]
- [Unverified claims]
- [Potential biases identified]
- [Logical fallacies]

**Biases Detected:**
- **Source Bias:** [description]
- **Political Bias:** [description]
- **Commercial Bias:** [description]
- **Omission Bias:** [what's left out]

**Logical Issues:**
- [Fallacy name]: [description]

**Factual Corrections Needed:**
1. [Claim] → [Correction needed]
   - Reason: [why correction is needed]
   - Search Query: [suggested search term]

## Research Findings

**Claim Verification:**
1. **[Original Claim]** - [Source in article]
   - **Verification Status:** ✓ Verified / ✗ False / ⚠ Unclear / ❓ Cannot verify
   - **Evidence:** [what external sources say]
   - **Conflicting Information:** [if other sources disagree]
   - **Search Terms Used:** [search queries]
   - **Reliable Sources:**
     - [Source 1]: [key information]
     - [Source 2]: [key information]

**Additional Context Found:**
- [Background information not in original]
- [Related events/timeline]
- [Expert opinions]
- [Statistical data]

**Corrections & Updates:**
- [Original statement] → [Corrected version]
- [Outdated information] → [Current status]
- [Missing details] → [Filled in information]

**Credibility Assessment:**
- **Overall Credibility:** [High/Medium/Low]
- **Source Trustworthiness:** [assessment]
- **Attribution Quality:** [Good/Poor/Missing]
- **Data Quality:** [Strong/Weak/Mixed]

## Recommendations for Final Story

**Must Address:**
- [Critical corrections needed]
- [Essential context to add]

**Should Address:**
- [Important clarifications]
- [Additional perspectives]

**Optional Enhancements:**
- [Nice-to-have additions]
- [Human interest angles]

**Search Queries Executed:**
1. [query] - [results]
2. [query] - [results]
```

**Configuration:**
- `search_enabled = true` (for web search)
- Model with larger context window (32K+)
- Higher `temperature = 0.4-0.5` for creative research

**Prompt Strategy:**
- First pass: Critique the structured graze output
- Second pass: Perform web searches for verification
- Third pass: Synthesize findings into structured format

**Note:** This combines chew (critique) + rehydrate (research) into a single stage to reduce pipeline complexity.

---

### 5. REMASTICATE (Renamed Distill)

**Purpose:** Write final polished news story
**Input:** `/app/output/regurgitate` (researched, critiqued articles)
**Output:** `/app/output/remasticate`
**Function:** Transform into publication-ready article

**Output Format:**

```markdown
# [Compelling Headline]

**Byline:** [Author if available, otherwise "Staff Report"]
**Dateline:** [CITY, Date] — [Lead paragraph]

[Lede paragraph with most important information]

## Body
[Well-structured narrative with:
- Clear nut graph (why this matters now)
- Supporting quotes and evidence
- Context and background
- Multiple perspectives
- Human elements if applicable]

## Key Points
- [Main takeaways in bullet format]

## Context
[Background information]
[Historical context if relevant]
[Broader significance]

## Sources
[Primary sources used]
[Expert attributions]
[Data sources]

---

**Research Notes:**
- [Key corrections made from original]
- [Additional information added]
- [Claims that could not be verified]
```

**Prompt Strategy:**
- Use regurgitate output as source material
- Incorporate critique and research findings
- Apply journalistic standards
- Remove metadata headers for publication
- Set `skip_metadata = true` in config

---

## Configuration Changes Needed

### New Pipeline Stages in config.ini:

```ini
[forage]
input_directory = /app/pastures
enabled = true
output_directory = /app/output/forage
# ... (existing settings)
append_input_to_output = false  # Changed from true

[graze]
input_directory = /app/output/forage
enabled = true
output_directory = /app/output/graze
# Standardize and extract
system_prompt_file = prompts/graze_system_v2.md
user_prompt_file = prompts/graze_user_v2.md
temperature = 0.3
max_tokens = 8192

[ferment]
input_directory = /app/output/graze
enabled = true
output_directory = /app/output/ferment
# Classify: Full story vs blurb
system_prompt_file = prompts/ferment_system.md
user_prompt_file = prompts/ferment_user.md
rejection_trigger_words = DECISION: BLURB
# Blurbs get .blurb.md marker
# Stories get .processed.md marker

[regurgitate]
input_directory = /app/output/ferment
enabled = true
output_directory = /app/output/regurgitate
# Critique + research combined
system_prompt_file = prompts/regurgitate_system.md
user_prompt_file = prompts/regurgitate_user.md
search_enabled = true
temperature = 0.4
max_tokens = 16384

[remasticate]
input_directory = /app/output/regurgitate
enabled = true
output_directory = /app/output/remasticate
# Write final story
system_prompt_file = prompts/remasticate_system.md
user_prompt_file = prompts/remasticate_user.md
temperature = 0.6
max_tokens = 4096
skip_metadata = true
```

---

## Code Changes Required

### Minor Changes (work within current architecture):
1. Create new prompt files for graze_v2, ferment, regurgitate, remasticate
2. Update config.ini with new stages
3. For ferment blurb handling: use file naming convention
   - Stories: `filename.processed.md`
   - Blurbs: `filename.blurb.md` (rejected marker)
   - Next stage only processes `.processed.md` files

### Major Changes (if needed later):
1. **Multiple output directories per stage** - add `output_directory_secondary` config
2. **Blurb list management** - append to blurb index file
3. **Parallel processing** - run critique and research concurrently

---

## Implementation Priority

**Phase 1: Quick Wins (No Code Changes)**
1. ✅ Backup prompts (DONE)
2. Create new graze_system_v2 prompt with structured extraction
3. Create ferment prompt with story/blurb classification
4. Create regurgitate prompt (combine chew + rehydrate)
5. Create remasticate prompt (update distill)
6. Update config.ini with new pipeline

**Phase 2: Pipeline Testing**
1. Test graze extraction quality
2. Test ferment classification accuracy
3. Test regurgitate research quality
4. Test remasticate final output

**Phase 3: Refinement**
1. Adjust prompts based on test results
2. Fine-tune importance scoring
3. Optimize token usage
4. Add blurb management if needed

---

## Next Steps

1. Review this design document
2. Approve or modify the standardized graze format
3. Approve or modify the ferment classification logic
4. Approve or modify regurgitate approach
5. Begin implementing Phase 1

---

## Questions for User Review

1. **Graze Format:** Does the structured metadata format capture everything needed? Any fields to add/remove?

2. **Ferment Classification:** Should blurb stories be completely rewritten or just summarized? Should they go to a separate folder?

3. **Blurb Management:** Do blurbs need to be collected into a single index file, or is individual file storage sufficient?

4. **Regurgitate Scope:** Is combining critique + research in one pass too complex? Should they remain separate?

5. **Importance Scoring:** What criteria should determine importance score? Currently thinking: novelty (1-3), impact (1-3), verifiability (1-3), depth (1-3)

6. **Token Management:** Graze extracting 15KB articles might hit limits. Should we strip HTML before sending to graze, or increase max_tokens significantly?

7. **Search Queries:** Should regurgitate autonomously perform web searches, or should it generate search queries for manual verification?

Let me know your thoughts on these, and I'll begin implementation!
