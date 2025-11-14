# TOMATITO VOICE AGENT - RAG IMPLEMENTATION GUIDE

## Overview

This guide explains how to implement the separated system prompt and RAG database files for the Tomatito Sexy Tapas Bar voice agent.

## File Structure

### System Prompt
**File:** `system_prompt.txt`
- Contains personality, tone, and behavioral instructions for Lenny
- Defines conversation flow and reservation process
- No menu-specific or location-specific content
- This is what you feed directly to your voice agent system

### RAG Database Files (10 Files)

All RAG files are in Markdown format for easy parsing and retrieval:

1. **rag_menu_overview.md** - ⭐ **START HERE** - Menu structure, navigation strategy, and cross-referencing guide
2. **rag_drinks_menu.md** - Drinks, beers, cocktails, and gin & tonic customization
3. **rag_tapas_pintxos.md** - Tapas and pintxos including the "Sexy Bites"
4. **rag_chef_recommendations.md** - Chef's recommended dishes with detailed descriptions
5. **rag_paellas.md** - Complete paella menu with cooking notes and traditions
6. **rag_fish_meat.md** - Fish and meat main courses (Pescados y Carnes)
7. **rag_sharing_plates.md** - Large format sharing dishes for groups
8. **rag_desserts.md** - Complete dessert menu (Dulce Tentación)
9. **rag_charcuterie_cheese.md** - Spanish cheese and charcuterie platters (Ala Carte)
10. **rag_locations_reservations.md** - All branch details, hours, and reservation information

## Implementation Strategy

### 1. System Prompt Integration

Load `system_prompt.txt` directly into your voice agent's system prompt:

```python
with open('system_prompt.txt', 'r') as f:
    system_prompt = f.read()
```

### 2. RAG Database Setup

**Option A: Vector Database (Recommended)**
```python
# Example using a vector database
from your_vector_db import VectorStore

# Initialize vector store
vector_store = VectorStore()

# Index all RAG files
rag_files = [
    'rag_menu_overview.md',  # Load this first - it's the navigation guide
    'rag_drinks_menu.md',
    'rag_tapas_pintxos.md',
    'rag_chef_recommendations.md',
    'rag_paellas.md',
    'rag_fish_meat.md',
    'rag_sharing_plates.md',
    'rag_desserts.md',
    'rag_charcuterie_cheese.md',
    'rag_locations_reservations.md'
]

for file in rag_files:
    with open(file, 'r') as f:
        content = f.read()
        # Chunk and index the content
        vector_store.index(content, metadata={'source': file})
```

**Option B: Simple Keyword Search**
```python
# For simpler implementation without vector DB
def load_rag_documents():
    documents = {}
    for file in rag_files:
        with open(file, 'r') as f:
            documents[file] = f.read()
    return documents

def search_rag(query, documents):
    # Simple keyword-based search
    relevant_docs = []
    keywords = query.lower().split()
    
    for filename, content in documents.items():
        content_lower = content.lower()
        if any(keyword in content_lower for keyword in keywords):
            relevant_docs.append(content)
    
    return relevant_docs
```

### 3. Query Processing Flow

```python
def process_user_query(user_message, conversation_history):
    # 1. Determine if RAG retrieval is needed
    needs_menu_info = detect_menu_query(user_message)
    needs_location_info = detect_location_query(user_message)
    
    # 2. Retrieve relevant context using hierarchical strategy
    context = ""
    
    if needs_menu_info:
        # Start with overview for broad queries or navigation
        if is_broad_menu_query(user_message):
            context += retrieve_document('rag_menu_overview.md')
        
        # Then get specific category information
        categories = identify_menu_categories(user_message)
        for category in categories:
            context += retrieve_category_info(category)
    
    if needs_location_info:
        context += retrieve_document('rag_locations_reservations.md')
    
    # 3. Construct prompt with context
    full_prompt = f"""
{system_prompt}

RELEVANT INFORMATION FROM KNOWLEDGE BASE:
{context}

CONVERSATION HISTORY:
{conversation_history}

USER: {user_message}

LENNY:
"""
    
    # 4. Generate response
    response = your_llm.generate(full_prompt)
    return response

def is_broad_menu_query(message):
    """Detect if user wants general menu overview"""
    broad_keywords = ['menu', 'what do you have', 'what can i order', 
                      'show me', 'tell me about your food', 'options']
    return any(keyword in message.lower() for keyword in broad_keywords)

def identify_menu_categories(message):
    """Map query to specific menu categories"""
    category_map = {
        'drinks': ['drink', 'cocktail', 'beer', 'gin', 'beverage'],
        'tapas': ['tapas', 'pintxos', 'appetizer', 'starter', 'small plate'],
        'paella': ['paella', 'rice'],
        'dessert': ['dessert', 'sweet', 'churros', 'cake'],
        # ... etc
    }
    
    categories = []
    message_lower = message.lower()
    for category, keywords in category_map.items():
        if any(keyword in message_lower for keyword in keywords):
            categories.append(category)
    
    return categories
```

## Query Detection Patterns

### Hierarchical Retrieval Strategy

**The menu_overview.md document serves as your navigation hub.** Use this two-tier approach:

**Tier 1: Menu Overview (rag_menu_overview.md)**
- Retrieve for broad menu questions
- Use for understanding menu structure and navigation
- Reference when customer asks "What do you have?" or "Tell me about your menu"
- Provides category summaries and cross-referencing framework

**Tier 2: Specific Category Documents**
- Retrieve after identifying specific interests from Tier 1
- Pull detailed information about individual dishes
- Use when customer asks about specific items or categories

**Example Flow:**
```
User: "What's on your menu?"
→ Retrieve: rag_menu_overview.md (full overview)
→ Present: Category structure and highlights

User: "Tell me more about the paellas"
→ Retrieve: rag_paellas.md (detailed paella info)
→ Present: Specific paella descriptions, timing, traditions

User: "Which paella pairs with white wine?"
→ Retrieve: rag_paellas.md + rag_drinks_menu.md
→ Present: Paella options with wine pairing recommendations
```

### Menu-Related Queries
Keywords to trigger menu information retrieval:
- Drinks: "drink", "cocktail", "beer", "gin", "tonic", "beverage"
- Food categories: "tapas", "paella", "dessert", "cheese", "meat", "fish"
- Specific dishes: "bombas", "churros", "wagyu", "cochinillo", etc.
- Questions: "what do you have", "menu", "what can I order", "recommendations"

### Location-Related Queries
Keywords to trigger location information:
- "location", "address", "where", "branch", "hours", "open", "close"
- "BGC", "Pasig", "Quezon City", "Estancia", "Opus"
- "reserve", "reservation", "book", "table"
- "parking", "directions", "how to get there"

### Reservation Process
Keywords that indicate reservation intent:
- "reserve", "book", "table", "reservation"
- "party of", "people", "guests"
- Date/time expressions: "tonight", "tomorrow", "Friday", "7pm"

## Enhanced RAG Features

### 1. Contextual Information
Each RAG file includes:
- **Detailed descriptions** - More context than basic menu listings
- **Flavor profiles** - Helps AI make recommendations
- **Pairing suggestions** - Wine/drink pairings
- **Cultural context** - Spanish traditions and background
- **Serving suggestions** - How many people, best practices
- **Chef's notes** - Special insights and tips

### 2. Cross-References
Files are designed to work together:
- Drinks file suggests pairings mentioned in food files
- Location file references dishes for special orders
- Dessert file mentions coffee from drinks menu

### 3. Structured for Retrieval
Each file uses:
- Clear markdown headers for chunking
- Consistent formatting for parsing
- Keywords repeated for better matching
- Section summaries for context

## Optimization Tips

### 1. Chunking Strategy
For vector databases, chunk by:
- Individual menu items (e.g., each paella separately)
- Complete sections (e.g., all "Sexy Bites" together)
- Recommended chunk size: 200-500 tokens

### 2. Metadata Tagging
Add metadata to chunks:
```python
{
    'source_file': 'rag_paellas.md',
    'category': 'main_course',
    'dish_name': 'Paella Negra',
    'price_range': 'medium',
    'dietary': ['seafood', 'gluten-free'],
    'serves': '2-3',
}
```

### 3. Retrieval Tuning
- Return top 2-3 most relevant chunks per query
- Combine similar results to avoid repetition
- Priority order: exact dish match > category match > general info

### 4. Response Generation
```python
# Provide focused context to avoid overwhelming the model
def generate_response(query, retrieved_context):
    # Limit context to most relevant 1000-1500 tokens
    focused_context = rank_and_limit(retrieved_context, max_tokens=1500)
    
    response = llm.generate(
        system_prompt=system_prompt,
        context=focused_context,
        user_query=query
    )
    return response
```

## Testing Queries

### Menu Queries to Test
```
1. "What drinks do you have?"
2. "Tell me about the paellas"
3. "What are your chef's recommendations?"
4. "Do you have desserts?"
5. "What's good for sharing among 4 people?"
6. "Tell me about the Wagyu"
7. "What are Sexy Bites?"
8. "Do you have vegetarian options?"
9. "What pairs well with seafood?"
10. "What's your most popular dish?"
```

### Location/Reservation Queries to Test
```
1. "Where are you located?"
2. "What are your hours?"
3. "I want to make a reservation"
4. "Do you have parking?"
5. "Which branch is closest to BGC?"
6. "Are you open on Sunday?"
7. "Can I book for a party of 8?"
8. "How do I get to your Pasig branch?"
```

### Complex Queries to Test
```
1. "I want to book a table at BGC for Friday at 7pm for 6 people"
2. "What would you recommend for someone who likes seafood? We're 4 people"
3. "Do you have any special dishes that need advance ordering?"
4. "I'm having a birthday party for 10 people, what do you recommend?"
```

## Performance Monitoring

Track these metrics:
1. **Retrieval accuracy** - Is the right information being retrieved?
2. **Response relevance** - Does Lenny answer the question correctly?
3. **Context usage** - Is retrieved information actually used in response?
4. **Latency** - Time from query to response
5. **User satisfaction** - Does the answer satisfy the user?

## Common Issues & Solutions

### Issue: Too much irrelevant information retrieved
**Solution:** Improve query classification, use more specific embeddings, add negative examples

### Issue: Missing information in response
**Solution:** Check if information exists in RAG files, improve retrieval threshold, ensure chunking doesn't split key info

### Issue: Response doesn't match Lenny's personality
**Solution:** Review system prompt clarity, ensure retrieved context doesn't override personality instructions

### Issue: Slow response times
**Solution:** Reduce chunk size, limit retrieval to top 2-3 results, pre-filter by category before semantic search

## Maintenance

### Regular Updates
- **Menu changes:** Update only relevant RAG files
- **Hours changes:** Update only locations file
- **New dishes:** Add to appropriate category file
- **Seasonal items:** Use metadata flags for easy filtering

### Version Control
Maintain versions of RAG files:
```
rag_files/
  v1.0/
    rag_paellas.md
    rag_drinks_menu.md
    ...
  v1.1/
    rag_paellas.md (updated)
    ...
```

## Advanced Features

### 1. Dynamic Recommendations
Use conversation context to provide personalized recommendations:
```python
def get_recommendations(user_preferences, conversation_history):
    # Extract preferences from conversation
    likes_spicy = "spicy" in conversation_history
    vegetarian = "vegetarian" in user_preferences
    
    # Filter and rank dishes
    recommendations = retrieve_filtered(
        dietary=["vegetarian"] if vegetarian else None,
        spice_level="high" if likes_spicy else None
    )
    return recommendations
```

### 2. Multi-turn Reservation
Track reservation state across multiple turns:
```python
reservation_state = {
    'name': None,
    'branch': None,
    'date': None,
    'time': None,
    'party_size': None,
    'contact': None
}

# Update as information is collected
# Prompt for missing fields
# Confirm when complete
```

### 3. Proactive Information
Offer relevant information based on query:
```python
if "paella" in query:
    additional_info = "Note: Paellas take 25-30 minutes to prepare. Would you like to order appetizers while you wait?"
```

## Integration Examples

### Example 1: n8n Workflow
```
1. Webhook receives voice input
2. Transcribe to text
3. Query classification node
4. RAG retrieval (if needed)
5. LLM generation with context
6. Text to speech
7. Return audio response
```

### Example 2: Chainlit Application
```python
@cl.on_message
async def main(message: cl.Message):
    # Retrieve context
    context = retrieve_context(message.content)
    
    # Generate response
    response = await generate_with_context(
        system_prompt,
        context,
        message.content
    )
    
    await cl.Message(content=response).send()
```

## Conclusion

This separation of system prompt and RAG database provides:
- ✅ **Flexibility:** Update menu without touching personality
- ✅ **Scalability:** Easy to add new menu items or locations
- ✅ **Maintainability:** Clear separation of concerns
- ✅ **Performance:** Efficient retrieval of only relevant information
- ✅ **Quality:** Rich, detailed information for better responses

The enhanced RAG files contain approximately 5-6x more information than the original prompt, providing much richer context for menu inquiries while keeping the system prompt clean and focused on behavior.
