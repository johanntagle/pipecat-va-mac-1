# TOMATITO RAG SYSTEM - QUICK REFERENCE GUIDE

## 📚 Document Hierarchy

```
system_prompt.txt
    ↓ (defines behavior and instructions)
    ↓
rag_menu_overview.md ⭐ NAVIGATION HUB
    ↓ (references and connects to)
    ↓
    ├─→ rag_drinks_menu.md
    ├─→ rag_tapas_pintxos.md
    ├─→ rag_chef_recommendations.md
    ├─→ rag_paellas.md
    ├─→ rag_fish_meat.md
    ├─→ rag_sharing_plates.md
    ├─→ rag_desserts.md
    ├─→ rag_charcuterie_cheese.md
    └─→ rag_locations_reservations.md
```

## 🎯 When to Use Each Document

| Document | Use When | Contains |
|----------|----------|----------|
| **system_prompt.txt** | Always loaded | Lenny's personality, behavior rules, reservation process |
| **rag_menu_overview.md** | "What's on the menu?", "Tell me about your food", broad menu questions | Menu structure, category summaries, navigation strategy, timing notes |
| **rag_drinks_menu.md** | Drinks, cocktails, beverages, "what can I drink?" | Full drinks menu, G&T customization, beer selection |
| **rag_tapas_pintxos.md** | Appetizers, starters, small plates, "Sexy Bites" | All tapas with descriptions and pairing notes |
| **rag_chef_recommendations.md** | "What do you recommend?", "What's popular?", "Best dishes?" | Patatas Bravas, Gambas al Ajillo, Sexy Chicken Fingers, Carpaccio |
| **rag_paellas.md** | Rice dishes, paella varieties, "traditional Spanish food" | All paellas with cooking times, traditions, socarrat explanation |
| **rag_fish_meat.md** | Main courses, seafood, meat dishes, Wagyu | Fish & Chips, A5 Wagyu, Salpicao, Callos, Flamenquin |
| **rag_sharing_plates.md** | Groups, celebrations, "something for 4+ people", family-style | Pollo Asado, Solomillo, Cochinillo, Chuleton |
| **rag_desserts.md** | End of meal, sweets, "dessert menu" | Volcan, Basque Cheesecake, Churros, Flan, ice cream |
| **rag_charcuterie_cheese.md** | Cheese boards, Spanish meats, grazing plates, wine pairings | Cheese platter, Cold cuts, Mixed platters |
| **rag_locations_reservations.md** | "Where are you?", hours, booking, "make a reservation" | All 3 locations, contact info, operating hours |

## 🔍 Retrieval Decision Tree

```
User Query
    │
    ├─ "What do you have?" / "Show me the menu"
    │   └─→ rag_menu_overview.md (full structure)
    │
    ├─ Mentions specific category (drinks, tapas, paella, etc.)
    │   └─→ Specific category document
    │
    ├─ "What do you recommend?"
    │   └─→ rag_menu_overview.md (recommendation framework)
    │       + rag_chef_recommendations.md (specific dishes)
    │
    ├─ Multiple categories (e.g., "food and drinks")
    │   └─→ Multiple documents (food category + drinks)
    │
    ├─ Location/hours/reservation question
    │   └─→ rag_locations_reservations.md
    │
    └─ Specific dish name
        └─→ Document containing that dish
```

## 💡 Smart Retrieval Patterns

### Pattern 1: Start Broad, Then Specific
```
User: "What should we order?"
Step 1: Retrieve rag_menu_overview.md → Get recommendation framework
Step 2: Ask follow-up → "How many people? Any preferences?"
Step 3: Retrieve specific categories based on response
```

### Pattern 2: Cross-Category Connections
```
User: "What goes well with the paella?"
Step 1: Retrieve rag_paellas.md → Paella details
Step 2: Retrieve rag_drinks_menu.md → Wine pairing suggestions
Step 3: Retrieve rag_tapas_pintxos.md → Pre-paella tapas suggestions
```

### Pattern 3: Time-Sensitive Information
```
User asks about dishes → Always check for timing notes in:
- rag_menu_overview.md (general timing guidance)
- rag_paellas.md (25-30 min cooking time)
- rag_desserts.md (10-15 min for some items)
- rag_sharing_plates.md (advance notice requirements)
```

## ⚠️ Critical Information Always in Context

These should ALWAYS be mentioned when relevant:

### Timing ⏰
- Paellas: 25-30 minutes
- Paella Cochinillo: 35-40 minutes  
- Volcan de Chocolate: 12-15 minutes
- Churros: 10-12 minutes

### Advance Orders 📋
- Cochinillo Segoviano: 24-48 hours notice
- Large groups (8+): 24 hours recommended

### Pricing 💰
- Always mention: "All prices are VAT inclusive and subject to 7.5% service charge"

### Serving Sizes 👥
- Paellas: 2-3 people (Cochinillo: 3-4)
- Sharing plates: 3-4 people minimum
- Tapas: Good for 2-4 people

## 🎨 Response Construction Guide

### For Broad Menu Questions
```
1. Load: rag_menu_overview.md
2. Present: Category overview with personality
3. Ask: "What sounds interesting to you?"
4. Prepare: To drill down into specific categories
```

### For Specific Item Questions
```
1. Load: Specific category document
2. Present: Detailed description (flavors, textures, portions)
3. Suggest: Pairings and complementary items
4. Mention: Any timing or special requirements
```

### For Recommendations
```
1. Load: rag_menu_overview.md (recommendation framework)
2. Consider: Group size, occasion, preferences
3. Load: Specific documents for recommended items
4. Present: Narrative recommendation with reasoning
```

### For Reservations
```
1. Load: rag_locations_reservations.md
2. Collect: Name, branch, date, time, party size, contact
3. Confirm: Read back all details
4. Provide: Branch-specific information
```

## 📊 Optimization Tips

### Context Window Management
**Priority Order for Limited Context:**
1. system_prompt.txt (always)
2. rag_menu_overview.md (for navigation)
3. Specific category documents (as needed)
4. rag_locations_reservations.md (if booking)

**Token Budget Strategy:**
- Overview: ~3,000 tokens
- Each category doc: ~2,500-4,000 tokens
- System prompt: ~800 tokens
- Reserve ~1,000 tokens for conversation history

### Caching Strategy (if supported)
Cache these frequently accessed documents:
- system_prompt.txt (always cached)
- rag_menu_overview.md (high access frequency)
- rag_locations_reservations.md (reservation queries)

### Query Classification
```python
def classify_query(message):
    """Returns: 'broad_menu', 'specific_category', 'location', 'reservation', 'specific_dish'"""
    
    # Broad menu keywords
    if any(kw in message.lower() for kw in ['what do you have', 'menu', 'options', 'show me']):
        return 'broad_menu'
    
    # Location/reservation keywords  
    if any(kw in message.lower() for kw in ['location', 'hours', 'reserve', 'book', 'address']):
        return 'location'
    
    # Specific categories
    categories = {
        'drinks': ['drink', 'cocktail', 'beer', 'wine'],
        'tapas': ['tapas', 'appetizer', 'starter'],
        'paella': ['paella', 'rice'],
        # ... etc
    }
    
    for category, keywords in categories.items():
        if any(kw in message.lower() for kw in keywords):
            return f'category_{category}'
    
    # Check for specific dish names
    # (would need a dish name database)
    
    return 'general'
```

## 🚀 Quick Start Checklist

- [ ] Load system_prompt.txt into agent configuration
- [ ] Index all 10 RAG markdown files in vector database
- [ ] Set up hierarchical retrieval (overview → specific)
- [ ] Implement query classification logic
- [ ] Configure cross-document retrieval for pairings
- [ ] Add timing and advance-order alerts
- [ ] Test with sample queries from each category
- [ ] Verify pricing disclaimer appears in responses

## 🧪 Test Queries by Priority

**Priority 1 - Must Work:**
- "What's on your menu?"
- "Tell me about the paellas"
- "I want to make a reservation"
- "What are your hours?"

**Priority 2 - Should Work Well:**
- "What do you recommend for 4 people?"
- "What drinks pair with seafood?"
- "Tell me about your cheese selection"
- "What desserts do you have?"

**Priority 3 - Nice to Have:**
- "Something quick for lunch"
- "What's authentically Spanish?"
- "I need to book for a large group"
- "What's your signature dish?"

## 📖 Document Size Reference

Approximate token counts for context management:

| Document | Tokens | Purpose |
|----------|--------|---------|
| system_prompt.txt | ~900 | Always loaded |
| rag_menu_overview.md | ~4,000 | Navigation hub |
| rag_drinks_menu.md | ~900 | Detailed category |
| rag_tapas_pintxos.md | ~1,500 | Detailed category |
| rag_chef_recommendations.md | ~1,500 | Detailed category |
| rag_paellas.md | ~2,200 | Detailed category |
| rag_fish_meat.md | ~2,000 | Detailed category |
| rag_sharing_plates.md | ~2,500 | Detailed category |
| rag_desserts.md | ~2,500 | Detailed category |
| rag_charcuterie_cheese.md | ~2,800 | Detailed category |
| rag_locations_reservations.md | ~3,000 | Location/booking |

**Total: ~23,800 tokens** (retrieve selectively, not all at once!)

## 🎯 Success Criteria

Your RAG system is working well when:
- ✅ Lenny maintains personality while being informative
- ✅ Responses include relevant timing information
- ✅ Pairings between food and drinks are suggested
- ✅ Portion sizes are mentioned when relevant
- ✅ Reservations collect all required information
- ✅ Broad questions get overview, specific questions get details
- ✅ No hallucinated menu items (only from RAG docs)
- ✅ Spanish cultural context is naturally woven in
