# TOMATITO SEXY TAPAS BAR - VOICE AGENT RAG SYSTEM

## 📁 Complete File Package

This package contains everything you need to implement a voice agent for Tomatito Sexy Tapas Bar with a clean separation between system behavior and knowledge base.

### System Configuration (1 file)
- **system_prompt.txt** - Core personality, behavior, and instructions for Lenny the concierge

### RAG Knowledge Base (10 files)
All files are in Markdown format optimized for retrieval and parsing:

1. **rag_menu_overview.md** ⭐ - Start here! Menu navigation hub and category guide
2. **rag_drinks_menu.md** - Drinks, beers, cocktails, customizable G&T
3. **rag_tapas_pintxos.md** - Tapas and "Sexy Bites" small plates
4. **rag_chef_recommendations.md** - Chef's signature dishes
5. **rag_paellas.md** - Traditional Spanish paellas with cooking notes
6. **rag_fish_meat.md** - Main courses including premium Wagyu
7. **rag_sharing_plates.md** - Large format dishes for groups
8. **rag_desserts.md** - Complete dessert menu
9. **rag_charcuterie_cheese.md** - Spanish cheese and meat platters
10. **rag_locations_reservations.md** - All locations, hours, booking info

### Documentation (3 files)
- **IMPLEMENTATION_GUIDE.md** - Technical implementation with code examples
- **QUICK_REFERENCE.md** - Decision trees and retrieval patterns
- **README.md** - This file

---

## 🎯 Key Features

### Enhanced Information Density
Each RAG document contains **5-6x more detail** than the original prompt, including:
- Detailed flavor profiles and textures
- Ingredient breakdowns
- Spanish cultural context and traditions
- Preparation methods and cooking times
- Serving sizes and portion guidance
- Pairing suggestions (food + drinks)
- Chef's notes and insider tips
- Dietary information
- Origin stories and authenticity notes

### Hierarchical Architecture
```
System Prompt (Behavior)
    ↓
Menu Overview (Navigation)
    ↓
Category Documents (Detailed Info)
    ↓
Cross-References (Pairings & Connections)
```

### Smart Retrieval Strategy
- **Broad queries** → Menu overview for structure
- **Specific queries** → Category documents for details
- **Recommendations** → Overview framework + specific items
- **Reservations** → Location document
- **Cross-category** → Multiple documents (e.g., food + drinks for pairing)

---

## 🚀 Quick Start

### 1. Load System Prompt
```python
with open('system_prompt.txt', 'r') as f:
    system_prompt = f.read()
```

### 2. Index RAG Documents
```python
# Using vector database (recommended)
from your_vector_db import VectorStore

vector_store = VectorStore()

# Start with overview for context
vector_store.index('rag_menu_overview.md', metadata={'type': 'overview', 'priority': 'high'})

# Then index category documents
categories = [
    'rag_drinks_menu.md',
    'rag_tapas_pintxos.md',
    'rag_chef_recommendations.md',
    'rag_paellas.md',
    'rag_fish_meat.md',
    'rag_sharing_plates.md',
    'rag_desserts.md',
    'rag_charcuterie_cheese.md'
]

for doc in categories:
    vector_store.index(doc, metadata={'type': 'category'})

# Finally, location info
vector_store.index('rag_locations_reservations.md', metadata={'type': 'location'})
```

### 3. Query Processing
```python
def handle_query(user_message):
    # Classify query type
    query_type = classify_query(user_message)
    
    # Retrieve relevant documents
    if query_type == 'broad_menu':
        context = retrieve('rag_menu_overview.md')
    elif query_type == 'specific_category':
        context = retrieve_category(user_message)
    elif query_type == 'reservation':
        context = retrieve('rag_locations_reservations.md')
    
    # Generate response with context
    response = generate_response(
        system_prompt=system_prompt,
        context=context,
        user_message=user_message
    )
    
    return response
```

---

## 📊 Document Structure Overview

### System Prompt (800 tokens)
**Purpose:** Define Lenny's personality and behavior
**Contains:**
- Introduction as Lenny
- Personality traits (warm, friendly, upbeat)
- How to handle menu inquiries (with RAG instructions)
- How to handle reservations (step-by-step process)
- Important reminders (pricing, timing, advance orders)

**Key Instruction:** References the RAG documents by name and explains when to use each

### Menu Overview (4,000 tokens)
**Purpose:** Navigation hub and menu structure guide
**Contains:**
- Restaurant concept and philosophy
- Complete menu category breakdown
- When to reference each specific document
- Recommendation frameworks
- Portion guidance and timing notes
- Common guest scenarios
- Cross-referencing strategy

**Use Case:** Start here for any menu-related query to understand structure

### Category Documents (900-3,000 tokens each)
**Purpose:** Detailed information about specific menu sections
**Contains:**
- Complete dish descriptions
- Flavor profiles and textures
- Ingredients and preparation methods
- Chef's notes and recommendations
- Pairing suggestions
- Cultural context
- Serving information
- Pricing tier indicators

**Use Case:** Deep dive into specific categories based on guest interest

### Location Document (3,000 tokens)
**Purpose:** All location and reservation information
**Contains:**
- 3 branch locations with full details
- Operating hours for each location
- Contact information (phone, email)
- Reservation process and requirements
- Parking and transportation info
- Special event booking
- FAQ section

**Use Case:** Any location, hours, or reservation query

---

## 🎨 Usage Patterns

### Pattern 1: First-Time Guest
```
User: "Hi, what do you have?"
System: 
  1. Retrieve: rag_menu_overview.md
  2. Present: Friendly category overview
  3. Ask: "What sounds interesting?"
  
User: "Tell me about the paellas"
System:
  1. Retrieve: rag_paellas.md
  2. Present: Paella varieties with details
  3. Mention: 25-30 minute cooking time
  4. Suggest: Tapas while waiting
```

### Pattern 2: Quick Recommendation
```
User: "What do you recommend for 4 people?"
System:
  1. Retrieve: rag_menu_overview.md (recommendation framework)
  2. Retrieve: rag_chef_recommendations.md
  3. Retrieve: rag_sharing_plates.md or rag_paellas.md
  4. Present: Structured recommendation with reasoning
```

### Pattern 3: Pairing Question
```
User: "What drinks go with seafood?"
System:
  1. Retrieve: rag_drinks_menu.md (wine pairing section)
  2. Retrieve: rag_fish_meat.md or rag_paellas.md (seafood items)
  3. Present: Specific pairings with explanation
```

### Pattern 4: Reservation
```
User: "I want to book a table"
System:
  1. Retrieve: rag_locations_reservations.md
  2. Follow: Reservation process from system prompt
  3. Collect: Name, branch, date, time, party size, contact
  4. Confirm: All details and provide branch info
```

---

## ⚠️ Critical Information

### Always Mention When Relevant:

**Timing ⏰**
- Paellas: 25-30 minutes cooking time
- Paella Cochinillo: 35-40 minutes
- Volcan de Chocolate: 12-15 minutes
- Churros: 10-12 minutes

**Advance Orders 📋**
- Cochinillo Segoviano: 24-48 hours notice required
- Large groups (8+): 24 hours recommended

**Pricing 💰**
- "All prices are VAT inclusive and subject to 7.5% service charge"

**Serving Sizes 👥**
- Mention how many people each dish serves
- Help guests order appropriate quantities

---

## 🔧 Implementation Options

### Option A: Vector Database (Recommended)
**Best for:** Production systems, complex queries, semantic search
**Tools:** Pinecone, Weaviate, Qdrant, ChromaDB
**Pros:** 
- Semantic similarity search
- Efficient retrieval
- Handles typos and variations
- Scalable

### Option B: Simple Keyword Search
**Best for:** MVPs, quick prototypes, simple use cases
**Tools:** Basic string matching, regex
**Pros:**
- Easy to implement
- No external dependencies
- Fast for small document sets
**Cons:**
- Less intelligent matching
- May miss relevant content

### Option C: Hybrid Approach
**Best for:** Balance of simplicity and intelligence
**Combines:** 
- Keyword classification for routing
- Vector search within categories
- Rule-based fallbacks

---

## 📈 Optimization Tips

### Context Window Management
**Token Budget:**
- System prompt: ~800 tokens (always)
- Menu overview: ~4,000 tokens (for broad queries)
- Category docs: ~2,500 tokens each (selective)
- Conversation history: ~1,000 tokens
- Total available: depends on your LLM (typically 4k-8k input)

**Strategy:**
- Always load system prompt
- Load overview for broad queries
- Load specific categories based on detected intent
- Limit to 2-3 category documents per query
- Prioritize most relevant content

### Caching Strategy
If your system supports prompt caching:
- Cache system_prompt.txt (static)
- Cache rag_menu_overview.md (high frequency)
- Cache rag_locations_reservations.md (frequent)
- Generate others on-demand

### Response Quality
- Use temperature 0.7-0.9 for personality
- Ensure retrieved context is actually used
- Validate responses contain timing/sizing info
- Check for hallucinations (items not in RAG docs)
- Monitor for off-brand tone

---

## 🧪 Testing

### Required Test Queries

**Menu Navigation:**
- [ ] "What's on your menu?"
- [ ] "Tell me about the paellas"
- [ ] "What drinks do you have?"

**Recommendations:**
- [ ] "What do you recommend?"
- [ ] "Something for 4 people?"
- [ ] "What's your signature dish?"

**Specific Items:**
- [ ] "Tell me about the Wagyu"
- [ ] "Do you have churros?"
- [ ] "What are Sexy Bites?"

**Pairings:**
- [ ] "What wine goes with paella?"
- [ ] "What should I have with seafood?"

**Reservations:**
- [ ] "I want to make a reservation"
- [ ] "What are your hours?"
- [ ] "Where are you located?"

**Complex Queries:**
- [ ] "Book table at BGC for Friday 7pm, 6 people"
- [ ] "Recommend a full meal for 4 seafood lovers"

---

## 🎓 Training & Customization

### Adding New Menu Items
1. Identify category (which RAG document?)
2. Follow existing format and structure
3. Include all standard fields (flavors, servings, pairings)
4. Update overview if adding new category
5. Re-index the modified document

### Updating Locations/Hours
1. Edit rag_locations_reservations.md only
2. Maintain consistent format
3. Update all affected branches
4. Re-index the document

### Adjusting Personality
1. Edit system_prompt.txt only
2. Keep RAG references intact
3. Test to ensure behavior change without knowledge loss

### Seasonal Menus
**Option 1:** Add seasonal markers to existing docs
**Option 2:** Create separate seasonal RAG files
**Option 3:** Use metadata tags for filtering

---

## 📚 Additional Resources

### Read These First
1. **QUICK_REFERENCE.md** - Decision trees and patterns
2. **IMPLEMENTATION_GUIDE.md** - Detailed technical guide
3. **system_prompt.txt** - Understand Lenny's instructions

### For Developers
- Review code examples in IMPLEMENTATION_GUIDE.md
- Understand query classification logic
- Study hierarchical retrieval pattern
- Implement error handling for missing info

### For Content Managers
- Learn document structure from existing files
- Follow formatting conventions for consistency
- Understand cross-referencing between documents
- Maintain tone and detail level when updating

---

## 🎯 Success Metrics

Your system is working well when:
- ✅ Responses sound like Lenny (personality maintained)
- ✅ Information is accurate (from RAG, not hallucinated)
- ✅ Timing notes are included when relevant
- ✅ Reservations collect all required information
- ✅ Pairings between food and drinks are suggested
- ✅ Portion sizes help guests order correctly
- ✅ No contradictions between documents
- ✅ Response time is acceptable (<2-3 seconds)

---

## 🐛 Troubleshooting

### Problem: Information not being retrieved
**Solution:** 
- Check query classification logic
- Verify documents are indexed correctly
- Test with simpler queries
- Check vector embedding quality

### Problem: Too much irrelevant information
**Solution:**
- Improve query classification
- Narrow retrieval to top 2-3 results
- Use hierarchical strategy (overview → specific)
- Add negative filtering

### Problem: Response doesn't match personality
**Solution:**
- Verify system prompt is always included
- Check if retrieved context overwhelms personality
- Adjust prompt structure
- Review temperature setting

### Problem: Missing timing information
**Solution:**
- Add explicit instructions in system prompt
- Include timing in RAG document structure
- Use post-processing to validate critical info
- Add timing to metadata tags

---

## 📞 Support & Maintenance

### Regular Updates
- **Weekly:** Check for menu changes
- **Monthly:** Review response quality
- **Quarterly:** Audit full document set
- **Yearly:** Major refresh and optimization

### Version Control
Maintain versions of your RAG documents:
```
rag_documents/
  v1.0/ (current)
  v1.1/ (staging)
  archive/
    v0.9/
```

### Monitoring
Track these metrics:
- Retrieval accuracy
- Response relevance  
- User satisfaction
- Query resolution rate
- Average response time
- Hallucination rate (items not in RAG)

---

## 📄 License & Usage

This system is designed specifically for Tomatito Sexy Tapas Bar. All content is fictional and created for demonstration purposes.

**Package Contents:**
- System prompt configuration
- 10 RAG knowledge base documents
- 3 implementation guides
- Code examples and patterns

**Total Package Size:** ~50,000 words of enhanced content

---

## 🚀 Next Steps

1. **Read QUICK_REFERENCE.md** for fast implementation patterns
2. **Review IMPLEMENTATION_GUIDE.md** for detailed technical setup
3. **Test with sample queries** from each category
4. **Customize** system prompt for your specific deployment
5. **Monitor and iterate** based on real user interactions

---

**Built with ❤️ for authentic Spanish tapas experiences**

*Version 1.0 - November 2024*
