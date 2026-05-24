import logging
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.output_parsers import OutputFixingParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from config import settings
from models.response import RestaurantIdea
from prompts.prompts import PromptBuilder
from utils import TextUtils, ValidationUtils, LoggingUtils

logger = logging.getLogger(__name__)


class LLMChainBuilder:
    """Builder for LangChain chains"""
    
    @staticmethod
    def get_llms() -> tuple:
        """Initialize creative and structured LLMs"""
        name_llm = ChatOpenAI(
            model=settings.MODEL_CREATIVE,
            temperature=settings.TEMP_CREATIVE,
            api_key=settings.openai_api_key,
            max_tokens=settings.max_tokens,
        )
        
        structured_llm = ChatOpenAI(
            model=settings.MODEL_STRUCTURED,
            temperature=settings.TEMP_STRUCTURED,
            api_key=settings.openai_api_key,
            max_tokens=settings.max_tokens,
        )
        
        return name_llm, structured_llm
    
    @staticmethod
    def build_name_chain():
        """Build chain for restaurant name generation"""
        name_llm, _ = LLMChainBuilder.get_llms()
        name_prompt = PromptBuilder.get_name_prompt()
        
        chain = (
            name_prompt
            | name_llm
            | StrOutputParser()
            | RunnableLambda(TextUtils.clean_text)
        )
        
        return chain
    
    @staticmethod
    def build_menu_chain():
        """Build chain for menu generation with auto-repair"""
        _, structured_llm = LLMChainBuilder.get_llms()
        
        base_parser = PydanticOutputParser(pydantic_object=RestaurantIdea)
        fixing_parser = OutputFixingParser.from_llm(
            parser=base_parser,
            llm=structured_llm
        )
        
        menu_prompt = PromptBuilder.get_menu_prompt()
        
        chain = (
            menu_prompt
            | structured_llm
            | fixing_parser
        )
        
        return chain
    
    @staticmethod
    def build_full_chain():
        """Build complete chain: name generation -> menu generation"""
        name_chain = LLMChainBuilder.build_name_chain()
        menu_chain = LLMChainBuilder.build_menu_chain()
        
        name_prompt = PromptBuilder.get_name_prompt()
        menu_prompt = PromptBuilder.get_menu_prompt()
        base_parser = PydanticOutputParser(pydantic_object=RestaurantIdea)
        
        full_chain = (
            {
                "cuisine": RunnablePassthrough(),
                "restaurant_name": name_chain,
            }
            | menu_prompt
            | RunnableLambda(lambda x: {
                **(x.dict() if hasattr(x, 'dict') else x),
                "format_instructions": base_parser.get_format_instructions()
            })
        )
        
        return full_chain


class RestaurantService:
    """Service layer for restaurant generation"""
    
    def __init__(self):
        """Initialize service with LLM chains"""
        self.name_chain = LLMChainBuilder.build_name_chain()
        self.menu_chain = LLMChainBuilder.build_menu_chain()
        logger.info("RestaurantService initialized")
    
    def generate(self, cuisine: str) -> RestaurantIdea:
        """
        Generate a restaurant concept for given cuisine
        
        Args:
            cuisine: Type of cuisine (e.g., 'Indian', 'Italian')
        
        Returns:
            RestaurantIdea: Generated restaurant with name and menu
        
        Raises:
            ValueError: If generation fails
        """
        LoggingUtils.log_generation_start(cuisine)
        
        try:
            # Step 1: Generate restaurant name
            logger.info(f"Generating name for {cuisine} cuisine")
            name = self.name_chain.invoke({"cuisine": cuisine})
            name = TextUtils.clean_text(name)
            
            if not ValidationUtils.validate_restaurant_name(name):
                raise ValueError(f"Generated invalid restaurant name: {name}")
            
            logger.info(f"Generated restaurant name: {name}")
            
            # Step 2: Generate menu with structured output
            logger.info(f"Generating menu for {name}")
            menu_prompt = PromptBuilder.get_menu_prompt()
            base_parser = PydanticOutputParser(pydantic_object=RestaurantIdea)
            
            _, structured_llm = LLMChainBuilder.get_llms()
            fixing_parser = OutputFixingParser.from_llm(
                parser=base_parser,
                llm=structured_llm
            )
            
            menu_chain = (
                menu_prompt
                | structured_llm
                | fixing_parser
            )
            
            result = menu_chain.invoke({
                "cuisine": cuisine,
                "restaurant_name": name,
                "format_instructions": base_parser.get_format_instructions()
            })
            
            # Ensure result is RestaurantIdea
            if isinstance(result, RestaurantIdea):
                restaurant = result
                # Override name with our generated one
                restaurant.name = name
            else:
                restaurant = RestaurantIdea(name=name, menu=result.menu)
            
            # Validation
            if not ValidationUtils.validate_menu_length(restaurant.menu):
                raise ValueError(
                    f"Invalid menu length: {len(restaurant.menu)} "
                    f"(expected 15)"
                )
            
            if not ValidationUtils.validate_menu_items(restaurant.menu):
                raise ValueError("Invalid menu items format")
            
            LoggingUtils.log_generation_success(
                cuisine, restaurant.name, len(restaurant.menu)
            )
            
            return restaurant
        
        except Exception as e:
            LoggingUtils.log_generation_error(cuisine, str(e))
            logger.error(f"Generation error: {e}", exc_info=True)
            raise ValueError(f"Failed to generate restaurant for {cuisine}: {str(e)}")
    
    def generate_batch(self, cuisines: list) -> dict:
        """
        Generate restaurants for multiple cuisines
        
        Args:
            cuisines: List of cuisine types
        
        Returns:
            dict: Results and failures
        """
        results = []
        failed = []
        
        for cuisine in cuisines:
            try:
                restaurant = self.generate(cuisine)
                results.append({
                    "cuisine": cuisine,
                    "restaurant": restaurant.model_dump()
                })
            except Exception as e:
                failed.append({
                    "cuisine": cuisine,
                    "error": str(e)
                })
        
        return {
            "results": results,
            "failed": failed,
            "total_generated": len(results),
            "total_failed": len(failed)
        }
