from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from typing import List


class PromptBuilder:
    """Builder for all prompt templates used in the application"""
    
    @staticmethod
    def get_name_prompt() -> PromptTemplate:
        """Prompt for generating creative restaurant names"""
        return PromptTemplate(
            input_variables=["cuisine"],
            template="""
You are a restaurant branding expert with 15 years of experience in the hospitality industry.
Your task is to suggest ONE premium, fancy, unique restaurant name for a {cuisine} cuisine establishment.

STRICT RULES:
- Return ONLY the restaurant name
- No explanations, no descriptions
- No prefixes like "Restaurant" or "The"
- No quotes or special formatting
- Must be catchy, memorable, and elegant
- Name should evoke the cuisine's essence
- Between 1-3 words only

Restaurant Name:""",
        )
    
    @staticmethod
    def get_menu_prompt() -> PromptTemplate:
        """Prompt for generating structured menu items"""
        return PromptTemplate(
            input_variables=["cuisine", "restaurant_name", "format_instructions"],
            template="""
You are a Michelin-star executive chef designing a premium restaurant concept.

Cuisine Type: {cuisine}
Restaurant Name: {restaurant_name}

Your task: Generate exactly 15 high-quality menu items that are:
- Authentic to the {cuisine} cuisine
- Aligned with the restaurant's brand and name
- A mix of appetizers, main courses, sides, and desserts
- Descriptive and appetizing
- Professional and upscale in presentation

Each menu item should be on a new line. Format them as just the item name (e.g., "Saffron Biryani" not "Biryani - A traditional rice dish with saffron").

{format_instructions}

Menu Items:""",
        )
    
    @staticmethod
    def get_validation_prompt() -> PromptTemplate:
        """Prompt for validating and fixing menu consistency"""
        return PromptTemplate(
            input_variables=["cuisine", "restaurant_name", "menu_items"],
            template="""
You are a restaurant consultant validating a menu for quality and coherence.

Restaurant: {restaurant_name}
Cuisine: {cuisine}
Current Menu Items:
{menu_items}

Review this menu and ensure:
1. All items are authentic to {cuisine} cuisine
2. No duplicate or very similar items
3. Good variety (appetizers, mains, sides, desserts)
4. All items fit the restaurant's concept

If any items are questionable, suggest replacements that maintain authenticity.
Output the final list of exactly 15 items, one per line.""",
        )
