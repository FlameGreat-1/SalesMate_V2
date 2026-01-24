from typing import List, Dict, Any, Optional
import json
from src.core.schemas.user import UserResponse
from src.core.schemas.profile import ProfileResponse
from src.core.schemas.product import ProductResponse


class PromptBuilder:
    
    BASE_SYSTEM_PROMPT = """You are an expert sales assistant for an electronics store.

ABSOLUTE RULES - NEVER VIOLATE:
1. ONLY recommend products from the inventory provided below
2. NEVER mention products not in the inventory
3. NEVER make up prices, specifications, or product details
4. If a product is not in inventory, say "We don't currently have that product in stock"
5. Use EXACT information from product data - do not guess or approximate

RESPONSE FORMAT RULES:
- Respond directly as the sales assistant
- NEVER say "Okay, here's..." or "I can help with that" or similar meta-commentary
- Just answer naturally as if you're speaking to the customer
- Example: Instead of "I can help with that. We have...", just say "We have..."

CONVERSATION CONTEXT RULES (ABSOLUTE PRIORITY - OVERRIDE EVERYTHING):
- ALWAYS read the conversation history FIRST before responding
- When customer is discussing a specific product, ALL follow-up questions refer to that EXACT same product
- IGNORE the detailed product list (Tier 2) if it shows different products than what customer is discussing
- ALWAYS cross-reference the full catalog (Tier 1) to find the EXACT product from conversation history
- Before providing ANY product information (specs, price, stock, features), perform this check:
  1. What product is the customer currently discussing? (check conversation history)
  2. Find that EXACT product by name in the full catalog (Tier 1)
  3. Use ONLY that product's data - never mix data from different products
- Understand ambiguous references ("it", "that", "this one", "the battery", "the price", "the storage") based on conversation flow
- Only switch products when customer explicitly asks about a different product by name
- NEVER use specifications from search results if they don't match the product being discussed

CRITICAL CONVERSATION RULES:
- ONLY discuss products the customer explicitly asked about
- If customer asks about laptops, talk ONLY about laptops
- If customer asks about a specific product, answer ONLY about that product
- DO NOT suggest unrelated products based on customer profile interests
- Suggesting related products is ONLY allowed when:
  * It directly relates to what the customer asked for (e.g., laptop accessories when discussing laptops)
  * It genuinely helps answer their question
  * Do this sparingly - not in every response
- Answer questions directly and concisely
- Ask questions sparingly - only when truly necessary to help the customer
- Avoid asking questions in every response
- Let the customer drive the conversation

PRICING AND DISCOUNTS (CRITICAL - NEVER VIOLATE):
- NEVER offer discounts beyond what's listed in product data
- NEVER calculate or promise bulk discounts
- NEVER make up promotional offers or price adjustments
- NEVER say "I can offer you X% off"
- You have ZERO authority to modify prices or create deals
- If customer asks about bulk discounts, say: "The current sale price is our best offer. We don't have additional bulk discounts available."
- If product has a discount, ONLY mention the existing discount percentage from product data
- NEVER do price calculations or show modified prices

BUDGET HANDLING:
- You do NOT know the customer's budget unless they tell you
- NEVER assume or mention a budget the customer hasn't stated
- When customer mentions budget: acknowledge it, show options within and slightly above
- When customer hasn't mentioned budget: present options, let them ask about pricing
- Customers often buy above their stated budget if value is clear

RESPONSE COMPLETENESS:
- When customer asks for comprehensive information, provide complete details, not partial
- Don't leave out important information that would help their decision
- Be thorough when customer requests full details

CONVERSATION FLOW:
- Maintain topic continuity - don't suggest switching topics unless customer explicitly changes subject
- Stay focused on what customer is currently discussing
- Answer questions about the current product directly

QUESTION DISCIPLINE:
- Prioritize being helpful over being interrogative
- Make informed recommendations rather than asking what they want
- Only ask questions when truly necessary to provide better help
- After initial greeting, minimize questions

Response style:
- Be conversational and helpful, not robotic
- Provide context and value, not just bare facts
- When stating price, mention if it's on sale and savings
- When confirming stock, add reassurance ("plenty available" or "limited stock")
- When describing products, include 1-2 key highlights that matter for their use case
- Answer directly but add helpful context
- Think like a helpful salesperson, not a database query
- Balance: informative but not overwhelming
- Use natural, conversational language
- Focus on what they asked, not what you think they might want
"""
    
    def build_system_prompt(
        self,
        user: UserResponse,
        profile: Optional[ProfileResponse],
        available_products: List[ProductResponse],
        conversation_stage: str = "discovery",
        full_catalog: Optional[List[ProductResponse]] = None
    ) -> str:
        """
        Build complete system prompt with TIER 1 (full catalog) and TIER 2 (detailed products).
        """
        prompt_parts = [self.BASE_SYSTEM_PROMPT]
        
        # TIER 1: Full catalog overview (30% info - all products)
        if full_catalog:
            prompt_parts.append(self._build_full_catalog(full_catalog))
        
        # Customer context
        prompt_parts.append(self._build_customer_context(user, profile))
        
        # TIER 2: Detailed product information (100% info - filtered products)
        if available_products:
            prompt_parts.append(self._build_detailed_product_context(available_products))
        
        # Stage-specific guidance
        prompt_parts.append(self._build_stage_guidance(conversation_stage, profile))
        
        return "\n\n".join(prompt_parts)
    
    def _build_full_catalog(self, products: List[ProductResponse]) -> str:
        """
        TIER 1: Build full catalog overview with 30% of product information.
        LLM knows ALL products exist and basic details.
        """
        catalog = "COMPLETE STORE INVENTORY (Tier 1 - Overview):\n"
        catalog += "="*80 + "\n"
        catalog += "You have access to ALL products below. Never say we don't have something if it's listed here.\n"
        catalog += "This is your complete product awareness. For detailed specs, refer to Tier 2 section.\n\n"
        
        for i, product in enumerate(products, 1):
            # Product name and brand
            catalog += f"{i}. {product.name} by {product.brand}\n"
            
            # Manufacturer if different from brand
            if product.manufacturer and product.manufacturer != product.brand:
                catalog += f"   Manufacturer: {product.manufacturer}\n"
            
            # Category and subcategory
            category_info = product.category
            if product.subcategory:
                category_info += f" > {product.subcategory}"
            catalog += f"   Category: {category_info}\n"
            
            # Pricing with discount info
            price_info = f"   Price: ${product.price:.2f}"
            if product.original_price and product.original_price > product.price:
                savings = product.original_price - product.price
                discount = product.discount_percentage or ((savings / product.original_price) * 100)
                price_info += f" (was ${product.original_price:.2f}, save ${savings:.2f} - {discount:.0f}% off)"
            catalog += price_info + "\n"
            
            # Price tier
            if product.price_tier:
                catalog += f"   Price Tier: {product.price_tier}\n"
            
            # Key features (top 3)
            if product.features:
                top_features = product.features[:3]
                catalog += f"   Key Features: {', '.join(top_features)}\n"
            
            # Stock status
            stock_info = f"   Stock: {product.stock_status}"
            if product.stock_quantity > 0:
                stock_info += f" ({product.stock_quantity} units)"
            catalog += stock_info + "\n"
            
            # Rating
            if product.rating:
                catalog += f"   Rating: {product.rating:.1f}/5.0 ({product.review_count} reviews)\n"
            
            # Target audience (who it's for)
            if product.target_audience:
                catalog += f"   Perfect for: {', '.join(product.target_audience[:3])}\n"
            
            # Use cases (what it's for)
            if product.use_cases:
                catalog += f"   Ideal for: {', '.join(product.use_cases[:3])}\n"
            
            # Product ID for reference
            catalog += f"   ID: {product.id}\n"
            
            # Tags for context
            if product.tags:
                catalog += f"   Tags: {', '.join(product.tags[:5])}\n"
            
            catalog += "\n"
        
        catalog += "="*80 + "\n"
        catalog += "IMPORTANT: This is your COMPLETE product catalog. When customer asks about a specific product,\n"
        catalog += "find it here by name, then use its EXACT details. For full specifications, check Tier 2 section.\n"
        
        return catalog


    def _build_customer_context(self, user: UserResponse, profile: Optional[ProfileResponse]) -> str:
        """
        Build customer profile context for personalization.
        """
        context_parts = [f"CUSTOMER PROFILE:\nEmail: {user.email}"]
        
        if profile:
            if profile.full_name:
                context_parts.append(f"Name: {profile.full_name}")
            
            if profile.budget_min or profile.budget_max:
                budget_info = "Budget: "
                if profile.budget_min and profile.budget_max:
                    budget_info += f"${profile.budget_min} - ${profile.budget_max}"
                elif profile.budget_max:
                    budget_info += f"Up to ${profile.budget_max}"
                elif profile.budget_min:
                    budget_info += f"From ${profile.budget_min}"
                context_parts.append(budget_info)
            
            if profile.preferred_categories:
                context_parts.append(f"\nBackground interests (DO NOT mention unless customer brings them up):")
                context_parts.append(f"- Categories: {', '.join(profile.preferred_categories[:5])}")
            
            if profile.preferred_brands:
                context_parts.append(f"- Preferred Brands: {', '.join(profile.preferred_brands[:5])}")
            
            if profile.feature_priorities:
                top_features = sorted(profile.feature_priorities.items(), key=lambda x: x[1], reverse=True)[:5]
                features_str = ', '.join([f[0] for f in top_features])
                context_parts.append(f"- Values: {features_str}")
        
        context_parts.append("\nHOW TO USE CUSTOMER DATA:")
        context_parts.append("1. Use budget to filter and prioritize recommendations when they ask for suggestions")
        context_parts.append("2. ONLY discuss products they explicitly ask about")
        context_parts.append("3. Do NOT mention their profile data unprompted (e.g., don't say 'based on your profile...')")
        context_parts.append("4. Answer their questions directly without suggesting unrelated products")
        context_parts.append("5. Ask questions sparingly - only when necessary")
        context_parts.append("6. Be concise and focused on their actual request")
        context_parts.append("\nUse this naturally. Don't reference 'profile' or 'data'.")
        
        return "\n".join(context_parts)
    
    def _build_detailed_product_context(self, products: List[ProductResponse]) -> str:
        """
        TIER 2: Build detailed product information with 100% of product data.
        LLM has COMPLETE knowledge of filtered products - can answer ANY question.
        """
        if not products:
            return ""
        
        context = "DETAILED PRODUCT INFORMATION (Tier 2 - Complete Specifications):\n"
        context += "="*80 + "\n"
        context += "These are the products relevant to the customer's request.\n"
        context += "You have COMPLETE information about these products - use it to answer ANY question.\n\n"
        
        for i, product in enumerate(products, 1):
            # Build complete product data dictionary with ALL fields
            product_data = {
                # Core Identity
                "product_id": product.id,
                "sku": product.sku,
                "name": product.name,
                "brand": product.brand,
                "manufacturer": product.manufacturer,
                
                # Classification
                "category": product.category,
                "subcategory": product.subcategory,
                "price_tier": product.price_tier,
                
                # Descriptions
                "description": product.description or "",
                "short_description": product.short_description or "",
                
                # Pricing
                "price": float(product.price),
                "original_price": float(product.original_price) if product.original_price else float(product.price),
                "discount_percentage": float(product.discount_percentage) if product.discount_percentage else 0.0,
                "currency": product.currency,
                
                # Inventory
                "stock_status": product.stock_status,
                "stock_quantity": product.stock_quantity,
                
                # Product Details
                "specifications": product.specifications,
                "features": product.features,
                "included_accessories": product.included_accessories,
                
                # Targeting & Classification
                "target_audience": product.target_audience,
                "use_cases": product.use_cases,
                "tags": product.tags,
                
                # Ratings & Reviews
                "rating": float(product.rating) if product.rating else 0.0,
                "review_count": product.review_count,
                
                # Policies
                "warranty_months": product.warranty_months,
                "return_policy_days": product.return_policy_days,
                
                # Status Flags
                "is_featured": product.is_featured,
                "is_new_arrival": product.is_new_arrival,
            }
            
            context += f"PRODUCT {i}:\n"
            context += json.dumps(product_data, indent=2)
            context += "\n\n" + "-"*80 + "\n\n"
        
        context += "="*80 + "\n"
        context += "CRITICAL: You have COMPLETE details above. Use EXACT information to answer questions about:\n"
        context += "- Specifications, features, what's included\n"
        context += "- Pricing, discounts, warranty, return policy\n"
        context += "- Stock availability, ratings, reviews\n"
        context += "- Who it's for (target_audience), what it's for (use_cases)\n"
        context += "NEVER make up or guess information - it's all provided above.\n"
        
        return context
    
    def _build_stage_guidance(self, stage: str, profile: Optional[ProfileResponse]) -> str:
        """
        Build stage-specific guidance for conversation flow.
        """
        stage_prompts = {
            "greeting": """STAGE: Initial Greeting
- Greet warmly and professionally
- Ask ONE simple question to understand their needs
- Keep it brief and natural
- Don't say "here's a greeting" - just greet them""",

            "discovery": """STAGE: Needs Discovery
- Answer their question directly
- Ask clarifying questions ONLY if critical information is missing
- DO NOT suggest unrelated products
- Focus ONLY on what they asked about
- Don't say "I can help with that" - just help
- Use conversation history to understand vague questions""",

            "recommendation": """STAGE: Product Recommendation
- Recommend 2-3 products that match what they asked for
- Use EXACT specs from product data
- If customer mentioned budget: acknowledge it, show options
- If no budget mentioned: present options, let them ask
- Avoid asking questions unless necessary
- DO NOT suggest products outside their request""",

            "comparison": """STAGE: Product Comparison
- Compare using EXACT specifications only
- Highlight key differences
- Be objective about pros/cons
- Answer directly without asking questions
- DO NOT suggest other products""",

            "objection_handling": """STAGE: Handling Concerns
- Address concerns honestly
- Provide alternatives from inventory ONLY if directly related
- Don't pressure
- Focus on resolving their specific concern
- Ask questions ONLY if necessary to understand the concern""",

            "closing": """STAGE: Closing
- Summarize recommended products
- Confirm fit with needs
- Explain next steps
- Thank them
- Answer directly without questions"""
        }
        
        return stage_prompts.get(stage, stage_prompts["discovery"])
    
    def build_greeting_prompt(self, user: UserResponse, profile: Optional[ProfileResponse]) -> str:
        """Build greeting stage prompt."""
        return self._build_stage_guidance("greeting", profile)
    
    def build_discovery_prompt(self, user: UserResponse, profile: Optional[ProfileResponse]) -> str:
        """Build discovery stage prompt."""
        return self._build_stage_guidance("discovery", profile)
    
    def build_recommendation_prompt(
        self,
        user: UserResponse,
        profile: Optional[ProfileResponse],
        products: List[ProductResponse]
    ) -> str:
        """Build recommendation stage prompt with product details."""
        parts = [
            self._build_stage_guidance("recommendation", profile),
            self._build_detailed_product_context(products)
        ]
        return "\n\n".join(parts)
    
    def build_comparison_prompt(
        self,
        user: UserResponse,
        profile: Optional[ProfileResponse],
        products: List[ProductResponse]
    ) -> str:
        """Build comparison stage prompt with product details."""
        parts = [
            self._build_stage_guidance("comparison", profile),
            self._build_detailed_product_context(products)
        ]
        return "\n\n".join(parts)


def get_prompt_builder() -> PromptBuilder:
    """Get PromptBuilder instance."""
    return PromptBuilder()
