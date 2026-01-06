# Rumen Content Processing Pipeline

A four-stage automated pipeline for transforming scraped web content into well-researched, verified news articles using LLMs and web search.

## Overview

The pipeline takes raw scraped content, cleans it, critiques it, verifies claims through web research, and assembles polished news articles - all with minimal human intervention.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RUMEN PROCESSING PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Scraped Content                                                            │
│       ↓                                                                     │
│  ┌──────────────────┐                                                       │
│  │   1. FORAGE      │  Content extraction and cleaning                      │
│  └────────┬─────────┘                                                       │
│           ↓                                                                 │
│  ┌──────────────────┐                                                       │
│  │   2. CHEW        │  Content critique and gap analysis                    │
│  └────────┬─────────┘                                                       │
│           ↓                                                                 │
│  ┌──────────────────┐                                                       │
│  │   3. REHYDRATE   │  Multi-source research with web search                 │
│  └────────┬─────────┘                                                       │
│           ↓                                                                 │
│  ┌──────────────────┐                                                       │
│  │   4. DIGEST      │  Article assembly and polish                          │
│  └────────┬─────────┘                                                       │
│           ↓                                                                 │
│  Polished News Article                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Stages

### Stage 1: Forage (Content Extraction & Cleaning)

**Purpose:** Transform noisy scraped web content into clean, structured markdown.

**Input:** Raw scraped HTML/markdown from `/app/pastures/`
**Output:** Cleaned articles in `/app/bolus/pastures/`

**What it does:**
- Extracts main content from scraped pages
- Removes navigation, ads, social media buttons
- Preserves author info, publication dates, quotes
- Identifies and classifies content quality
- Handles error pages (404s, paywalls, etc.)

**Key Features:**
- YAML frontmatter with metadata
- Structured summary at top
- Clean article body
- Error classification for problematic content

**Model:** `nvidia/nemotron-3-nano-30b-a3b:free`
**Temperature:** 0.3 (deterministic extraction)
**Max Tokens:** 4096

**Output Example:**
```markdown
---
title: Extracted Title
author: Author Name
publication_date: 2026-01-06
quality_score: 8/10
---

## Content Summary
**Overview**: [2-3 sentence summary]
**Key Points**: [3-5 bullet points]

## [Cleaned Article Title]
[Cleaned article body...]
```

---

### Stage 2: Chew (Content Critique & Gap Analysis)

**Purpose:** Analyze content quality, identify biases, logical fallacies, and research gaps.

**Input:** Cleaned forage output from `/app/bolus/pastures/`
**Output:** Comprehensive critique in `/app/bolus/chew/`

**What it does:**
- Grades content quality (A-F)
- Analyzes logical structure
- Identifies bias and perspective issues
- Assesses factual claims
- Finds completeness gaps
- Recommends improvements
- **Preserves full original article** at end

**Key Features:**
- Overall quality grade with detailed rationale
- Bias analysis (political, cultural, emotional)
- Logical fallacy detection
- Research roadmap (what to investigate)
- Full original content preserved in Section 11

**Model:** `nvidia/nemotron-3-nano-30b-a3b:free`
**Temperature:** 0.4 (analytical but creative)
**Max Tokens:** 6144

**Output Example:**
```markdown
## Overall Grade: B+

### Logical Structure
[Analysis of argument flow...]

### Bias & Perspective
[Identification of biases...]

### Factual Claims Assessment
[Verification status of claims...]

### Research Roadmap
[What needs to be investigated...]

## 11. Original Content
[Full article preserved]
```

---

### Stage 3: Rehydrate (Multi-Source Research & Verification)

**Purpose:** Fill research gaps, verify claims, gather expert opinions, and build context using web search.

**Input:** Critique from `/app/bolus/chew/`
**Output:** Comprehensive research package in `/app/bolus/rehydrate/`

**What it does:**
- Cross-references claims across multiple sources
- Uses web search to find expert opinions
- Gathers historical, political, economic context
- Verifies statistics and data
- Builds timelines
- Identifies key players and entities
- Presents multiple perspectives on contentious issues
- **NEW:** Includes Section 0 with article summary

**Key Features:**
- **10 standardized sections** (consistent structure)
- **Verification status labels:** VERIFIED, PARTIALLY VERIFIED, UNVERIFIED, DISPUTED, DEBUNKED
- **Temporal prioritization:** Recent sources override early skepticism
- **Source quality assessment**
- **Table format** for easy parsing

**Model:** `nvidia/nemotron-3-nano-30b-a3b:free:online` (with web search)
**Temperature:** 0.3 (factual accuracy)
**Max Tokens:** 16384

**Output Structure:**
```markdown
## 0. Article Summary
[2-3 sentences summarizing original article]

## 1. Verified Claims
| Claim | Status | Evidence | Confidence |
|-------|--------|----------|------------|

## 2. Conflicting Reports & Perspectives
| Issue | Perspective A | Perspective B | Assessment |

## 3. Expert Opinions
| Expert | Credentials | Opinion | Source |

## 4. Historical & Contextual Background
### 4.1 Historical Context
### 4.2 Political Context
### 4.3 Economic Context
### 4.4 Geopolitical Context

## 5. Statistics & Data
| Data Point | Value | Source | Date |

## 6. Timeline & Chronology
| Date | Event | Significance | Sources |

## 7. Key Players & Entities
### 7.1 Individuals
### 7.2 Organizations
### 7.3 Countries/Regions

## 8. What Could Not Be Verified
| Claim | Research Attempts | Outcome | Confidence |

## 9. Research Summary & Quality Assessment
### 9.1 Completeness Assessment
### 9.2 Source Quality Overview
### 9.3 Key Findings
### 9.4 Limitations
```

**Verification Standards:**
- **VERIFIED:** 3+ major outlets OR official docs/court records
- **PARTIALLY VERIFIED:** Core confirmed, details unclear
- **UNVERIFIED:** ZERO credible sources found
- **DISPUTED:** Credible sources actively contradict
- **DEBUNKED:** Multiple sources prove it false

---

### Stage 4: Digest (Article Assembly & Polish)

**Purpose:** Transform research packages into polished, engaging news articles.

**Input:** Research from `/app/bolus/rehydrate/`
**Output:** Final news articles in `/app/bolus/digest/`

**What it does:**
- Synthesizes verified facts into narrative
- Integrates expert opinions naturally
- Weaves in context and statistics
- Presents multiple perspectives fairly
- Attributed disputed claims appropriately
- Creates engaging lead and conclusion

**Key Features:**
- Professional journalism tone
- Compelling headlines and leads
- Proper source attribution
- Balanced presentation of contentious issues
- 800-1500 word articles
- NO web search needed (uses rehydrate research)

**Model:** `nvidia/nemotron-3-nano-30b-a3b:free`
**Temperature:** 0.7 (engaging but factual)
**Max Tokens:** 8192

**Output Example:**
```markdown
# Compelling Headline

[City/Location] – [Lead paragraph with who, what, when, where, why.]

[Nut graph explaining broader significance.]

[Body paragraphs weaving verified facts, expert opinions,
statistics, and context into engaging narrative.]

[For contentious issues:]
While [Perspective A], [Perspective B] suggests...

[Conclusion with forward-looking perspective.]

---

**Sources:** [Summary of source types]
```

**Writing Principles:**
- **VERIFIED claims** → Present as fact
- **PARTIALLY VERIFIED** → Use qualifying language ("may include", "appears to be")
- **DISPUTED claims** → Attribute to sources ("While X claims, Y reports...")
- **UNVERIFIED claims** → Omit or explicitly label as unverified

---

## File Naming Convention

The pipeline uses hash-based chaining to track the origin and processing history of each file.

**Pattern:**
```
[stage]_precedingStage1_precedingStage2_[content_hash]_[timestamp1]_[timestamp2]_[timestamp3].md
```

**Example:**
```
digest_rehydrate_chew_forage_
a1b2c3d4e5f6...
_20260106_201638
_20260106_201736
_20260106_202102
.md
```

**Breakdown:**
- `digest` - Current stage
- `rehydrate_chew_forage` - Preceding stages (processing history)
- `a1b2c3d4e5f6...` - SHA-256 hash of original content
- `20260106_201638` - Timestamp when forage processed (Jan 6, 2026, 20:16:38)
- `20260106_201736` - Timestamp when chew processed
- `20260106_202102` - Timestamp when rehydrate processed

This chaining:
1. **Prevents duplicate processing** (same content hash won't be re-processed)
2. **Maintains provenance** (can trace back to original source)
3. **Tracks timing** (know exactly when each stage ran)
4. **Enables debugging** (see the full processing history)

---

## Configuration

All stages are configured in `config/config.ini`:

```ini
[DEFAULT]
# Default settings for all stages
provider = openrouter
model = nvidia/nemotron-3-nano-30b-a3b:free
temperature = 0.7
max_tokens = 2048
retry_attempts = 3
retry_delay = 2

[forage]
input_directory = /app/pastures
enabled = true
delete_input_files = false
system_prompt_file = prompts/forage_system.md
user_prompt_file = prompts/forage_user.md
provider = openrouter
model = nvidia/nemotron-3-nano-30b-a3b:free
temperature = 0.3
max_tokens = 4096
output_directory = /app/bolus/pastures

[chew]
input_directory = /app/bolus/pastures
enabled = true
delete_input_files = false
system_prompt_file = prompts/chew_system.md
user_prompt_file = prompts/chew_user.md
provider = openrouter
model = nvidia/nemotron-3-nano-30b-a3b:free
temperature = 0.4
max_tokens = 6144
output_directory = /app/bolus/chew

[rehydrate]
input_directory = /app/bolus/chew
enabled = true
delete_input_files = false
system_prompt_file = prompts/rehydrate_system.md
user_prompt_file = prompts/rehydrate_user.md
provider = openrouter
model = nvidia/nemotron-3-nano-30b-a3b:free:online
temperature = 0.3
max_tokens = 16384
output_directory = /app/bolus/rehydrate

[digest]
input_directory = /app/bolus/rehydrate
enabled = true
delete_input_files = false
system_prompt_file = prompts/digest_system.md
user_prompt_file = prompts/digest_user.md
provider = openrouter
model = nvidia/nemotron-3-nano-30b-a3b:free
temperature = 0.7
max_tokens = 8192
output_directory = /app/bolus/digest
```

**Model Choices:**
- **`:online` suffix** = Enables web search (only for rehydrate stage)
- **Without `:online`** = Standard inference (cheaper, faster)
- **Nemotron 30B** = Free tier, good quality, ~4K context window
- **Temperature** = Lower (0.3-0.4) for factual work, higher (0.7) for creative

---

## Usage

### Automatic Processing

1. **Add content** to `/app/pastures/` (or subdirectories)
2. Pipeline **automatically detects** new files
3. **Sequential processing**: forage → chew → rehydrate → digest
4. **Final output** appears in `/app/bolus/digest/`

### Monitoring

```bash
# View logs
./run-docker.sh logs

# Check processing status
docker exec rumen ls -lh /app/bolus/*/$(date +%Y/%m/%d)/

# View web interface
http://localhost:8000/viewer/
```

### Manual Trigger

If you need to reprocess files:

1. **Unmark as processed** by editing filenames or moving files
2. **Restart monitoring** or wait for next scan interval (5 seconds)

### Disabling Stages

To disable specific stages, edit `config/config.ini`:

```ini
[forage]
enabled = false  # Won't process new forage files
```

---

## Directories

```
/app/
├── pastures/              # Input: Raw scraped content
│   ├── worldnews/
│   ├── jewishpolitics/
│   └── [other sources]/
│
├── bolus/                 # All processing outputs
│   ├── pastures/          # Stage 1: Forage output
│   ├── chew/              # Stage 2: Chew output
│   ├── rehydrate/         # Stage 3: Rehydrate output
│   └── digest/            # Stage 4: Final articles
│
└── viewer/                # Web interface (auto-generated)
```

**Organized by date:**
```
/app/bolus/[stage]/YYYY/MM/DD/[filename].md
```

---

## Prompt Files

Each stage has two prompt files in `prompts/`:

1. **`[stage]_system.md`** - Defines the AI's role, capabilities, and standards
2. **`[stage]_user.md`** - Provides specific instructions and output structure

**Current Prompts:**
- `forage_system.md` + `forage_user.md` → Content extraction
- `chew_system.md` + `chew_user.md` → Content critique
- `rehydrate_system.md` + `rehydrate_user.md` → Research & verification
- `digest_system.md` + `digest_user.md` → Article assembly

---

## Key Design Decisions

### 1. Rehydrate-Only Digest (Not Chew + Rehydrate)

**Decision:** Digest reads only rehydrate output, not chew output.

**Rationale:**
- Rehydrate now includes **Section 0: Article Summary**
- Smaller input size (~30K vs ~105K tokens)
- Works with Nemotron's context window (no need for GLM-4.5-Air)
- Simpler pipeline (no file matching needed)
- Rehydrate already flags disputed/biased claims

**Trade-off:**
- ❌ Loses full original article body
- ❌ Loses detailed critique analysis
- ✅ But creates fresh article anyway, so not needed

### 2. Standardized Rehydrate Output

**Decision:** Enforce strict 10-section structure with tables.

**Rationale:**
- Consistent parsing for digest stage
- Predictable structure for programmatic access
- Easier to debug and validate
- Prevents "creative" deviations

**Result:**
- All rehydrate outputs follow identical format
- Digest can reliably extract specific information
- Quality is more consistent

### 3. Verification Thresholds

**Decision:** Clear, strict rules for verification status.

**Rationale:**
- Prevents over-skepticism (marking everything "unverified")
- Temporal prioritization (recent > old)
- Multiple source requirement
- Official sources carry weight

**Impact:**
- More accurate verification of breaking news
- Better handling of evolving stories
- Clear distinction between "not found" and "disputed"

### 4. Cost Optimization

**Decision:** Only rehydrate stage uses `:online` model (web search).

**Rationale:**
- Web search costs ~$0.02 per request
- Redundant searches on retries waste money
- Implemented smart retry: strips `:online` after empty response

**Result:**
- 50% cost savings on retry scenarios
- Search happens once, content generation retries without search

---

## Quality Assurance

### Verification Standards

**VERIFIED:**
- 3+ major news outlets (Reuters, AP, BBC, CNN, NBC, NYT, Guardian)
- OR official government statements
- OR court documentation
- OR direct video evidence from credible sources

**Example:** Maduro's capture was VERIFIED because:
- Multiple major outlets reported it
- Court appearance confirmed
- Video evidence available
- Recent sources (Jan 5) overrode early skepticism (Jan 3)

**DISPUTED:**
- Credible sources actively contradict each other
- Genuine debate among experts
- NOT just early skepticism + later confirmation

**Example:** "Most antisemitism comes from the left" is DISPUTED because:
- FBI data shows significant right-wing involvement
- Credible sources disagree
- Not just early uncertainty

### Temporal Prioritization

**Rule:** Recent sources override early skepticism

**Example Pattern:**
```
Jan 3: "Cannot verify Maduro capture" → Early skepticism
Jan 4: "Reports of capture but unconfirmed" → Emerging
Jan 5: "Maduro appears in court" → VERIFIED
```

**Result:** Mark as VERIFIED, not DISPUTED or UNVERIFIED.

### Source Quality

**High Credibility:**
- Major news agencies (Reuters, AP, BBC)
- Official government publications
- Court documentation
- Academic institutions
- International organizations (UN, ICJ)

**Medium Credibility:**
- Commercial news with editorial standards
- Think tanks (note political leaning)
- Industry publications

**Low Credibility:**
- Partisan publications (note bias)
- Social media (verify with primary sources)
- Anonymous sources (corroborate)

---

## Performance Characteristics

### Processing Time

Per article (approximate):
- **Forage:** 13-20 seconds
- **Chew:** 20-30 seconds
- **Rehydrate:** 30-90 seconds (includes web search)
- **Digest:** 40-60 seconds

**Total:** ~2-4 minutes per article through full pipeline

### Token Usage

Approximate per article:
- **Forage:** Input ~3K, Output ~2K tokens
- **Chew:** Input ~5K, Output ~5K tokens
- **Rehydrate:** Input ~8K, Output ~10K tokens
- **Digest:** Input ~15K, Output ~4K tokens

### File Sizes

- **Raw scraped:** 5-15KB
- **Forage output:** 8-12KB
- **Chew output:** 20-30KB (includes original content)
- **Rehydrate output:** 15-18KB (standardized 10 sections)
- **Digest output:** 5-10KB (800-1500 word article)

---

## Troubleshooting

### Common Issues

**1. Files not processing:**
- Check logs: `./run-docker.sh logs`
- Verify stage is `enabled = true` in config
- Ensure input directory path is correct

**2. Rehydrate cutoffs:**
- Increase `max_tokens` in config (currently 16384)
- Check if `:online` model is being used

**3. Empty responses:**
- Nemotron sometimes returns empty responses
- Automatic retry will handle this
- If persistent, model may be overloaded

**4. Verification too strict:**
- Review `rehydrate_system.md` verification standards
- Check temporal prioritization rules
- Ensure recent sources are prioritized

**5. High costs:**
- Only rehydrate uses web search (`:online`)
- Check retry optimization is working (logs should show "Retrying without :online")
- Consider disabling rehydrate if verification not needed

---

## Web Interface

Auto-generated HTML viewer at http://localhost:8000/viewer/

**Features:**
- Browse outputs by stage
- Filter by date
- View formatted markdown
- Download individual files

---

## Development History

**Phase 1: Three-Stage Pipeline**
- Implemented: Forage → Chew → Rehydrate
- Purpose: Clean, critique, and verify content

**Phase 2: Verification Enhancement**
- Enhanced prompts with clear verification standards
- Added temporal prioritization rules
- Fixed "over-skepticism" issue

**Phase 3: Standardization**
- Enforced strict 10-section structure for rehydrate
- Added Section 0: Article Summary
- Table formats for consistency

**Phase 4: Digest Stage**
- Implemented fourth stage for article assembly
- Decision: Rehydrate-only input (simpler, cheaper)
- Professional journalism output

**Phase 5: Cost Optimization**
- Smart retry logic to avoid redundant web searches
- Strip `:online` suffix after empty response
- 50% savings on retry scenarios

---

## Future Enhancements

### Potential Improvements

1. **Multiple Output Formats**
   - Blog posts, podcast scripts, video scripts
   - Social media threads
   - Executive summaries

2. **Quality Metrics**
   - Automatic scoring of output quality
   - Comparison to human-written articles
   - A/B testing of prompts

3. **Parallel Processing**
   - Process multiple articles simultaneously
   - Faster throughput for large batches

4. **Customizable Styles**
   - Different journalistic voices (AP style, NYT style, etc.)
   - Tone adjustments (formal, casual, technical)
   - Audience targeting (general, expert, mixed)

5. **Feedback Loop**
   - Human-in-the-loop validation
   - Learning from corrections
   - Adaptive prompt tuning

---

## Technical Stack

**Language:** Python 3.11+
**Framework:** FastAPI
**LLM Provider:** OpenRouter
**Models:** NVIDIA Nemotron-3-Nano-30B-A3B (free tier)
**Container:** Docker + Docker Compose
**Monitoring:** Inotify file watching

**Key Dependencies:**
- `openai` - OpenAI-compatible API client
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `watchdog` - File monitoring
- `python-dotenv` - Environment configuration

---

## License

See LICENSE file for details.

---

## Contributing

This is a personal project, but suggestions and improvements are welcome through GitHub issues.

---

**Last Updated:** January 6, 2026
**Version:** 1.0.0
**Status:** Production Ready ✅
