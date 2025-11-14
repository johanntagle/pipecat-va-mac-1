# TOMATITO RAG SYSTEM ARCHITECTURE

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                               │
│                    "What should we order?"                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY CLASSIFICATION                          │
│  • Detect intent (menu/location/reservation)                    │
│  • Identify categories (drinks/food/specific items)             │
│  • Determine specificity (broad/specific/recommendation)        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   [BROAD MENU]      [SPECIFIC ITEM]    [RESERVATION]
        │                  │                  │
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Retrieve   │   │   Retrieve   │   │   Retrieve   │
│   Overview   │   │   Category   │   │   Location   │
│   Document   │   │   Document   │   │   Document   │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CONTEXT ASSEMBLY                                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ system_prompt.txt (always loaded)                      │    │
│  │ + Retrieved RAG document(s)                            │    │
│  │ + Conversation history                                 │    │
│  │ + User query                                           │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM GENERATION                                │
│  • Generate response as Lenny                                   │
│  • Use retrieved context for facts                              │
│  • Maintain personality from system prompt                      │
│  • Include timing/sizing/pricing when relevant                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE OUTPUT                               │
│  "Great question! For your group of 4, I'd recommend            │
│   starting with our Bombas de Jamon and Gambas al Ajillo        │
│   while we prepare a Paella El Chiringuito (takes 25-30 min).   │
│   Perfect pairing with our house white wine!"                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Document Relationship Map

```
                     ┌─────────────────────┐
                     │  system_prompt.txt  │
                     │   (ALWAYS LOADED)   │
                     └──────────┬──────────┘
                                │
                                │ references
                                │
                                ▼
                ┌───────────────────────────────┐
                │   rag_menu_overview.md        │
                │   (NAVIGATION HUB)            │
                │   • Menu structure            │
                │   • Category summaries        │
                │   • Recommendation framework  │
                │   • Cross-references          │
                └───────────┬───────────────────┘
                            │
                            │ links to
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   DRINKS     │    │    FOOD      │    │  LOCATION    │
└──────┬───────┘    └──────┬───────┘    └──────────────┘
       │                   │
       │                   │
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ rag_drinks_  │    │ rag_tapas_   │
│   menu.md    │    │  pintxos.md  │
└──────────────┘    └──────┬───────┘
                            │
                    ┌───────┼────────┐
                    │       │        │
                    ▼       ▼        ▼
            ┌──────────┐ ┌──────┐ ┌──────────┐
            │  chef_   │ │paella│ │  fish_   │
            │  recomm  │ │  s   │ │  meat    │
            └──────────┘ └──────┘ └──────────┘
                    │       │        │
                    └───────┼────────┘
                            │
                    ┌───────┼────────┐
                    │       │        │
                    ▼       ▼        ▼
            ┌──────────┐ ┌──────┐ ┌──────────┐
            │ sharing_ │ │desert│ │ charcut  │
            │  plates  │ │  s   │ │  erie    │
            └──────────┘ └──────┘ └──────────┘
```

---

## Query Type Decision Tree

```
                        USER QUERY
                            │
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Menu Related │ │  Location/   │ │     Other    │
    │              │ │ Reservation  │ │              │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           │                │                │
           │                ▼                ▼
           │         ┌─────────────┐   ┌─────────────┐
           │         │  Retrieve   │   │   General   │
           │         │  Location   │   │ Conversation│
           │         │     Doc     │   │   (system   │
           │         └─────────────┘   │   prompt)   │
           │                           └─────────────┘
           │
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│ Broad  │   │Specific│
│  Menu  │   │Category│
└────┬───┘   └───┬────┘
     │           │
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Overview │ │Category │
│   Doc   │ │   Doc   │
└─────────┘ └────┬────┘
                 │
         ┌───────┼───────┐
         │       │       │
         ▼       ▼       ▼
     ┌──────┐┌──────┐┌──────┐
     │Drinks││Tapas ││Paella│
     └──────┘└──────┘└──────┘
         │       │       │
         └───────┼───────┘
                 │
                 ▼
         ┌──────────────┐
         │ More Options │
         │ (Fish, Meat, │
         │  Sharing,    │
         │  Desserts)   │
         └──────────────┘
```

---

## Hierarchical Retrieval Strategy

```
LEVEL 0: System Prompt (Always Active)
│
├─ Personality: Lenny (warm, friendly, upbeat)
├─ Behavior Rules: How to interact
├─ Process Guidelines: Reservations, recommendations
└─ RAG Instructions: When and how to use knowledge base
    │
    ▼
LEVEL 1: Menu Overview (Broad Context)
│
├─ Restaurant Concept
├─ Menu Structure (all categories)
├─ Navigation Strategy
├─ Recommendation Frameworks
└─ Cross-Referencing Guide
    │
    ▼
LEVEL 2: Category Documents (Specific Details)
│
├─ Individual Dishes
│   ├─ Descriptions
│   ├─ Ingredients
│   ├─ Flavors & Textures
│   └─ Preparation Methods
│
├─ Serving Information
│   ├─ Portion Sizes
│   ├─ Cooking Times
│   └─ Advance Orders
│
├─ Cultural Context
│   ├─ Spanish Traditions
│   ├─ Origin Stories
│   └─ Authenticity Notes
│
└─ Recommendations
    ├─ Pairings
    ├─ Chef's Tips
    └─ Ordering Suggestions
```

---

## Context Assembly Process

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: CLASSIFY QUERY                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Input: "What drinks go with seafood?"                   │ │
│ │ Classification: menu_pairing                            │ │
│ │ Categories: drinks + seafood                            │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: RETRIEVE DOCUMENTS                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ rag_drinks_menu.md → wine pairing section              │ │
│ │ rag_fish_meat.md → seafood dishes                      │ │
│ │ rag_paellas.md → seafood paellas                       │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: ASSEMBLE CONTEXT                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [system_prompt.txt] ~800 tokens                        │ │
│ │ + [rag_drinks_menu.md excerpt] ~500 tokens             │ │
│ │ + [rag_fish_meat.md excerpt] ~600 tokens               │ │
│ │ + [conversation history] ~300 tokens                   │ │
│ │ = TOTAL: ~2,200 tokens                                 │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: GENERATE RESPONSE                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ LLM receives:                                           │ │
│ │ • System prompt (Lenny's personality)                  │ │
│ │ • Relevant wine pairing info                           │ │
│ │ • Seafood dish details                                 │ │
│ │ • User's question                                      │ │
│ │                                                         │ │
│ │ Generates:                                             │ │
│ │ Natural response combining all context                 │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Token Budget Visualization

```
┌────────────────────────────────────────────────────────────┐
│ AVAILABLE CONTEXT WINDOW: ~8,000 tokens (example)         │
└────────────────────────────────────────────────────────────┘

ALLOCATION:
│
├─ System Prompt (Fixed): 800 tokens [██████]
│  Always loaded, defines Lenny
│
├─ Conversation History: 500-1000 tokens [████]
│  Recent exchanges for context
│
├─ Retrieved Context: 2,000-4,000 tokens [████████████]
│  │
│  ├─ Overview (broad queries): ~4,000 tokens
│  │  OR
│  ├─ Single category: ~2,500 tokens
│  │  OR  
│  └─ Multiple categories: ~1,000 tokens each
│
├─ User Query: 50-200 tokens [█]
│  Current question
│
└─ Reserved for Response: 1,000-2,000 tokens [████]
   Generated answer

STRATEGY:
• Prioritize most relevant documents
• Limit to 2-3 category docs per query
• Use overview for structure, categories for detail
• Cache frequently used documents if possible
```

---

## Multi-Turn Conversation Flow

```
TURN 1: Exploration
User: "What's on your menu?"
     │
     ├─ Load: rag_menu_overview.md
     ├─ Present: Category overview
     └─ Ask: "What interests you?"

TURN 2: Category Selection
User: "Tell me about paellas"
     │
     ├─ Load: rag_paellas.md
     ├─ Present: Paella varieties
     ├─ Mention: 25-30 min cooking time
     └─ Suggest: Order tapas while waiting

TURN 3: Pairing Question
User: "What should we have while it cooks?"
     │
     ├─ Context: User interested in paella
     ├─ Load: rag_tapas_pintxos.md
     ├─ Load: rag_drinks_menu.md (pairing section)
     └─ Present: Tapas + drink recommendations

TURN 4: Finalize Order
User: "Let's get the Paella Negra and Bombas"
     │
     ├─ Confirm: Order details
     ├─ Remind: 25-30 min wait, tapas first
     ├─ Retrieve: Serving size info
     └─ Ask: "Anything else or ready to reserve?"

TURN 5: Reservation
User: "Yes, book for tomorrow at 7pm, 3 people"
     │
     ├─ Load: rag_locations_reservations.md
     ├─ Collect: Name, branch, contact
     └─ Confirm: Complete reservation
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│ USER QUERY                                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
            ┌──────────────┐
            │  Classify    │
            │    Query     │
            └──────┬───────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
    ┌────────┐          ┌────────┐
    │Success │          │ Unclear│
    └───┬────┘          └───┬────┘
        │                   │
        │                   ▼
        │            ┌──────────────┐
        │            │  Clarifying  │
        │            │   Question   │
        │            └──────┬───────┘
        │                   │
        │                   └─────────┐
        ▼                             │
    ┌────────────┐                    │
    │  Retrieve  │                    │
    │    Docs    │◄───────────────────┘
    └──────┬─────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│ Found  │   │Not     │
│        │   │Found   │
└───┬────┘   └───┬────┘
    │            │
    │            ▼
    │     ┌──────────────┐
    │     │  Fallback    │
    │     │  Response    │
    │     └──────┬───────┘
    │            │
    └────────────┴─────────┐
                           │
                           ▼
                    ┌──────────────┐
                    │   Generate   │
                    │   Response   │
                    └──────────────┘
```

---

## Performance Optimization

```
COLD START (No Cache)
│
├─ Load System Prompt: 50ms
├─ Query Classification: 100ms
├─ Retrieve Documents: 200ms
├─ Embed & Search: 300ms
├─ LLM Generation: 1500ms
└─ TOTAL: ~2150ms (2.15s)

WARM START (With Cache)
│
├─ System Prompt: 0ms (cached)
├─ Query Classification: 100ms
├─ Retrieve Documents: 50ms (cached)
├─ Embed & Search: 100ms (cached vectors)
├─ LLM Generation: 1500ms
└─ TOTAL: ~1750ms (1.75s)

OPTIMIZATION STRATEGIES:
│
├─ Cache system prompt (static content)
├─ Cache menu_overview (high frequency)
├─ Cache embeddings for all documents
├─ Pre-load frequently accessed categories
└─ Use streaming for faster perceived response
```

---

## Maintenance Workflow

```
┌────────────────────────────────────────────────────────┐
│                   CONTENT UPDATE                        │
└──────────────────────┬─────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │New Menu  │  │ Hours    │  │  System  │
  │   Item   │  │ Change   │  │  Tweak   │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │             │              │
       ▼             ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Edit    │  │  Edit    │  │   Edit   │
  │Category  │  │Location  │  │  System  │
  │   Doc    │  │   Doc    │  │  Prompt  │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │             │              │
       └─────────────┼──────────────┘
                     │
                     ▼
            ┌────────────────┐
            │   Re-index     │
            │   Documents    │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │  Test Queries  │
            └────────┬───────┘
                     │
            ┌────────┴────────┐
            │                 │
            ▼                 ▼
       ┌─────────┐       ┌─────────┐
       │ Success │       │  Issues │
       └────┬────┘       └────┬────┘
            │                 │
            │                 ▼
            │          ┌──────────┐
            │          │   Fix &  │
            │          │  Retest  │
            │          └────┬─────┘
            │               │
            └───────────────┘
                     │
                     ▼
            ┌────────────────┐
            │    Deploy      │
            └────────────────┘
```

---

**System Architecture Summary:**
- **Modular Design:** Separate behavior from knowledge
- **Hierarchical Retrieval:** Overview → Category → Details
- **Intelligent Routing:** Query type determines document selection
- **Context Optimization:** Smart token budget management
- **Scalable Structure:** Easy to maintain and update

