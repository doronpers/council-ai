"""
Council AI - Usage Examples

This file demonstrates various ways to use the Council AI package.
"""

import asyncio
from council_ai import Council, get_persona, list_personas, get_domain, list_domains
from council_ai.core.persona import Persona, PersonaCategory, Trait
from council_ai.core.council import ConsultationMode


# ═══════════════════════════════════════════════════════════════════════════════
# Basic Usage
# ═══════════════════════════════════════════════════════════════════════════════

def example_basic():
    """Basic council consultation."""
    # Create a council for business decisions
    council = Council.for_domain("business", api_key="your-api-key")
    
    # Consult the council
    result = council.consult("Should we expand into the European market?")
    
    # Print the synthesis
    print("=== SYNTHESIS ===")
    print(result.synthesis)
    print()
    
    # Print individual responses
    print("=== INDIVIDUAL RESPONSES ===")
    for response in result.responses:
        print(f"\n{response.persona.emoji} {response.persona.name}:")
        print(response.content)


# ═══════════════════════════════════════════════════════════════════════════════
# Custom Council Assembly
# ═══════════════════════════════════════════════════════════════════════════════

def example_custom_council():
    """Assemble a custom council with specific personas."""
    council = Council(api_key="your-api-key", provider="anthropic")
    
    # Add specific members
    council.add_member("rams")      # Design perspective
    council.add_member("holman")    # Security perspective
    council.add_member("grove")     # Strategy perspective
    
    # Adjust weights
    council.set_member_weight("grove", 1.5)  # More influence for strategy
    
    # Consult
    result = council.consult(
        query="Review our new authentication system design",
        context="We're building a B2B SaaS with sensitive financial data",
    )
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Different Consultation Modes
# ═══════════════════════════════════════════════════════════════════════════════

def example_modes():
    """Demonstrate different consultation modes."""
    council = Council.for_domain("startup", api_key="your-api-key")
    query = "Should we pivot from B2C to B2B?"
    
    # Individual - each member responds separately
    print("=== INDIVIDUAL MODE ===")
    result = council.consult(query, mode=ConsultationMode.INDIVIDUAL)
    for r in result.responses:
        print(f"{r.persona.name}: {r.content[:200]}...")
    
    # Debate - multiple rounds of discussion
    print("\n=== DEBATE MODE ===")
    result = council.consult(query, mode=ConsultationMode.DEBATE)
    print(result.synthesis)
    
    # Vote - members vote on the decision
    print("\n=== VOTE MODE ===")
    result = council.consult(query, mode=ConsultationMode.VOTE)
    for r in result.responses:
        print(f"{r.persona.name}: {r.content}")


# ═══════════════════════════════════════════════════════════════════════════════
# Creating Custom Personas
# ═══════════════════════════════════════════════════════════════════════════════

def example_custom_persona():
    """Create and use a custom persona."""
    # Create a custom persona
    product_expert = Persona(
        id="product_expert",
        name="Product Sage",
        title="Product Strategy Expert",
        emoji="📱",
        category=PersonaCategory.ADVISORY,
        core_question="Does this serve a real user need better than alternatives?",
        razor="Build what users need, not what they say they want. Observe behavior, not opinions.",
        traits=[
            Trait(name="User Empathy", description="Deep understanding of user needs", weight=1.5),
            Trait(name="Market Awareness", description="Knowledge of competitive landscape", weight=1.2),
            Trait(name="Prioritization", description="Ability to focus on what matters", weight=1.3),
        ],
        focus_areas=["User Research", "Product-Market Fit", "Roadmap Strategy", "Feature Prioritization"],
    )
    
    # Create council with custom persona
    council = Council(api_key="your-api-key")
    council.add_member(product_expert)
    council.add_member("kahneman")  # Add built-in for cognitive perspective
    council.add_member("grove")     # Add built-in for strategic perspective
    
    # Consult
    result = council.consult("Should we add social features to our productivity app?")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Domain-Specific Examples
# ═══════════════════════════════════════════════════════════════════════════════

def example_code_review():
    """Code review example."""
    council = Council.for_domain("coding", api_key="your-api-key")
    
    code = '''
    def process_payment(user_id, amount, card_token):
        user = db.get_user(user_id)
        if user.balance >= amount:
            charge = stripe.charge(card_token, amount)
            user.balance -= amount
            db.save(user)
            return {"success": True, "charge_id": charge.id}
        return {"success": False, "error": "Insufficient funds"}
    '''
    
    result = council.consult(
        query=f"Review this payment processing code:\n\n```python{code}```",
        context="This is for a fintech application handling real money",
    )
    
    return result


def example_career_decision():
    """Career decision example."""
    council = Council.for_domain("career", api_key="your-api-key")
    
    result = council.consult("""
    I'm deciding between two job offers:
    
    Option A: Senior Engineer at Google
    - $350k total comp
    - Stable, great benefits
    - Limited ownership
    
    Option B: Founding Engineer at YC startup
    - $180k + 1.5% equity
    - High risk/reward
    - Full ownership of technical decisions
    
    I'm 32, married, no kids, have 6 months savings.
    """)
    
    return result


def example_creative_project():
    """Creative project example."""
    council = Council.for_domain("creative", api_key="your-api-key")
    council.add_member("treasure")  # Add sonic lens for audio
    
    result = council.consult("""
    I'm creating a meditation app.
    
    Key decisions needed:
    1. Voice style for guided meditations
    2. Background soundscapes
    3. Session length defaults
    4. Visual design approach
    
    Target audience: stressed professionals, 25-45
    """)
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Async Usage
# ═══════════════════════════════════════════════════════════════════════════════

async def example_async():
    """Async consultation for better performance."""
    council = Council.for_domain("business", api_key="your-api-key")
    
    # Async consult
    result = await council.consult_async(
        "What are the key risks in our expansion plan?"
    )
    
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Using Hooks for Custom Processing
# ═══════════════════════════════════════════════════════════════════════════════

def example_hooks():
    """Use hooks to customize behavior."""
    council = Council.for_domain("business", api_key="your-api-key")
    
    # Pre-consult hook: add context
    def add_company_context(query, context):
        company_context = "Company: TechCorp, Industry: SaaS, Stage: Series B"
        full_context = f"{company_context}\n\n{context}" if context else company_context
        return query, full_context
    
    council.add_pre_consult_hook(add_company_context)
    
    # Response hook: add formatting
    def format_response(persona, content):
        return f"[{persona.category.value.upper()}] {content}"
    
    council.add_response_hook(format_response)
    
    # Now all consultations will have company context
    result = council.consult("Should we raise a Series C?")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Listing Available Resources
# ═══════════════════════════════════════════════════════════════════════════════

def example_list_resources():
    """List available personas and domains."""
    print("=== AVAILABLE PERSONAS ===")
    for persona in list_personas():
        print(f"{persona.emoji} {persona.id}: {persona.name} - {persona.title}")
    
    print("\n=== AVAILABLE DOMAINS ===")
    for domain in list_domains():
        print(f"  {domain.id}: {domain.name}")
        print(f"    Personas: {', '.join(domain.default_personas)}")


# ═══════════════════════════════════════════════════════════════════════════════
# Export Results
# ═══════════════════════════════════════════════════════════════════════════════

def example_export():
    """Export results in different formats."""
    council = Council.for_domain("business", api_key="your-api-key")
    result = council.consult("What should our Q1 priorities be?")
    
    # Markdown export
    markdown = result.to_markdown()
    with open("consultation_result.md", "w") as f:
        f.write(markdown)
    
    # JSON export
    import json
    json_data = result.to_dict()
    with open("consultation_result.json", "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    
    print("Results exported!")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # List available resources (doesn't require API key)
    example_list_resources()
    
    # Uncomment to run examples (requires API key):
    # example_basic()
    # example_custom_council()
    # example_modes()
    # example_custom_persona()
    # example_code_review()
    # example_career_decision()
    # example_creative_project()
    # asyncio.run(example_async())
    # example_hooks()
    # example_export()
