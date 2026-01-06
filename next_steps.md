# Next Steps: Article Assembly Stage

## Current Pipeline Status

The three-stage content processing pipeline is complete and working well:

1. **Forage** ✅ - Content extraction and cleaning
2. **Chew** ✅ - Content critique and gap analysis
3. **Rehydrate** ✅ - Multi-source research with web search

## What We Have Now

### Rehydrate Outputs Contain ✅

- **Comprehensive verified facts** with sources and confidence levels
- **Expert opinions** with credentials, affiliations, and direct quotes
- **Timeline & chronology** with event sequence analysis
- **Historical/political/economic/social/geopolitical context** (4 types of context)
- **Key players & entities** (individuals, organizations, countries)
- **Multiple perspectives** on contentious issues with source attribution
- **Statistics & data** with source verification
- **Brief quotes** from original content ("What the Original Content Said")
- **Research quality assessment** with completeness evaluation

Example structure from rehydrate output:
- Section 1: Verified Claims (VERIFIED/PARTIALLY VERIFIED/UNVERIFIED/DISPUTED/DEBUNKED)
- Section 2: Conflicting Reports & Perspectives
- Section 3: Expert Opinions
- Section 4: Historical & Contextual Background
- Section 5: Statistics & Data
- Section 6: Timeline & Chronology
- Section 7: Key Players & Entities
- Section 8: Multiple Perspectives on Key Issues
- Section 9: What Could Not Be Verified
- Section 10: Research Summary & Quality Assessment

### Rehydrate Does NOT Contain ❌

- **Full original article body** (only brief quotes are preserved)
- **Original narrative structure** and story flow
- **Original quotes in full context**
- **Critique analysis** (what was biased, logical fallacies, gaps to address)

### Chew Outputs Contain ✅

- **Complete content critique** with:
  - Overall grade (A-F)
  - Logical structure analysis
  - Bias & perspective analysis
  - Factual claims assessment
  - Completeness analysis
  - Recommendations for improvement
- **Full original article preserved** at the end (section 11)
- **Research roadmap** for what to investigate

## ✅ IMPLEMENTED: Fourth Stage - "Digest"

### Status: COMPLETE ✅

The digest stage has been implemented and is ready to use!

### Design Decision: Rehydrate Only ✅ FINAL CHOICE

After analysis, we chose to use **rehydrate output alone** for the digest stage.

**Rationale:**
- ✅ Rehydrate now includes Section 0: Article Summary (2-3 sentences)
- ✅ Rehydrate contains all verified facts, expert opinions, context, data
- ✅ Much smaller input size (~30K tokens vs ~105K for rehydrate+chew)
- ✅ Works with Nemotron's context window (no need for GLM-4.5-Air)
- ✅ Simpler pipeline (no file matching needed)
- ✅ Faster processing and lower costs

**What we're NOT losing:**
- Original narrative structure (digest creates fresh article)
- Critique analysis (rehydrate already flagged disputed/biased claims)
- Full original quotes (rehydrate has key quotes from original)

### Implementation Details

**Configuration:**
```ini
[digest]
input_directory = /app/bolus/rehydrate
enabled = true
system_prompt_file = prompts/digest_system.md
user_prompt_file = prompts/digest_user.md
provider = openrouter
model = nvidia/nemotron-3-nano-30b-a3b:free
temperature = 0.7
max_tokens = 8192
output_directory = /app/bolus/digest
```

**Key Features:**
1. **Single Input**: Reads only rehydrate output (no chew needed)
2. **Article Assembly**: Transforms research into polished news articles
3. **Verification Handling**: Treats VERIFIED as fact, PARTIALLY VERIFIED with qualifiers, DISPUTED with attribution
4. **Quality Standards**: Professional journalism tone, proper source attribution, balanced perspectives
5. **Narrative Focus**: Engaging lead, nut graph, contextual depth, strong conclusion

**Output Format:**
- Compelling headline
- Lead paragraph (5 W's)
- Body with verified facts, expert opinions, statistics, context
- Multiple perspectives on contentious issues
- Forward-looking conclusion
- 800-1500 words

### Files Created

1. ✅ `prompts/digest_system.md` - Expert journalist role, synthesis methods, quality standards
2. ✅ `prompts/digest_user.md` - Detailed article structure, writing guidelines, quality checklist
3. ✅ Updated `config/config.ini` - Added [digest] section

### How It Works

**Pipeline Flow:**
```
Pastures (scraped content)
    ↓
Forage (cleaned content) - Section 0 summary added here
    ↓
Chew (critique + gaps) - NOT used by digest
    ↓
Rehydrate (research + verification) ← Digest reads this
    ↓
Digest (polished article) ← FINAL OUTPUT
```

**Input/Output:**
- **Input**: `rehydrate_chew_forage_*.md` (~15-18KB, 10 standardized sections)
- **Output**: `digest_rehydrate_chew_forage_*.md` (polished news article)

### Testing

To test the digest stage:
1. Ensure rehydrate files exist in `/app/bolus/rehydrate/`
2. Digest will automatically process them
3. Review output in `/app/bolus/digest/`

**Expected Results:**
- Well-researched, professionally written articles
- Verified facts presented as fact
- Disputed claims attributed appropriately
- Expert opinions integrated naturally
- Context and statistics woven in
- Engaging narrative flow

---

## ARCHIVED: Alternative Approaches Considered

#### Option 1: Rehydrate Only ⚠️ ← **CHOSEN**
**Pros:** Verified facts, smaller inputs, simpler pipeline, works with Nemotron
**Cons:** Loses original narrative voice (but digest creates fresh voice)
**Best for:** Writing new articles from research ✅ SELECTED

#### Option 2: Rehydrate + Chew ❌ NOT CHOSEN
**Pros:** Original structure, critique warnings, full quotes
**Cons:** 105K tokens (requires GLM-4.5-Air), complex file matching
**Best for:** Improving existing articles (decided against this approach)

## Current Limitations & Considerations

### Context Window
- Chew files are ~75K tokens (with original content preserved)
- Rehydrate files are ~30K tokens
- Combined: ~105K tokens
- Need model with 128K+ context window (GLM-4.5-Air: 131K ✅)

### Model Choice
- **Free option**: `z-ai/glm-4.5-air:free:online` (131K context)
- **Paid option**: Larger models if needed (GPT-4, Claude 3.5 Sonnet)

### Processing Flow
```
Rehydrate file → Identify hash → Find matching chew file → Load both → Generate article
```

## Testing Plan

1. Create digest_system.md and digest_user.md prompts
2. Add [digest] section to config.ini
3. Test with one rehydrate + chew pair
4. Review output quality
5. Iterate on prompts
6. Expand to multiple output formats

## Priority Actions

1. ✅ Three-stage pipeline working
2. ✅ Enhanced verification standards implemented
3. ✅ Web search integration functional
4. ⏳ **NEXT**: Design and implement digest stage
5. ⏳ Support multiple output formats
6. ⏳ Add quality metrics and evaluation

## Success Criteria

Digest stage should produce:
- Well-researched articles with verified facts
- Balanced presentation of multiple perspectives
- Proper source attribution
- Engaging narrative structure
- Avoidance of biased/problematic elements identified in critique
- Rich context from rehydrate research
- Appropriate tone for target audience
