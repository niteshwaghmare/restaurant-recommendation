import logging
from fastapi import APIRouter, HTTPException

from models.request import GenerateRestaurantRequest, BatchGenerateRestaurantRequest
from models.response import GenerateRestaurantResponse, BatchGenerateResponse
from services.llm_service import RestaurantService

logger = logging.getLogger(__name__)

router = APIRouter()
service = RestaurantService()


@router.post(
    "/generate",
    response_model=GenerateRestaurantResponse,
    summary="Generate a restaurant concept",
    description="Generate a unique restaurant name and menu for a given cuisine type"
)
async def generate_restaurant(request: GenerateRestaurantRequest) -> GenerateRestaurantResponse:
    """
    Generate a restaurant concept with name and 15-item menu
    
    **Parameters:**
    - `cuisine`: Type of cuisine (e.g., 'Italian', 'Indian', 'Japanese')
    
    **Returns:**
    - Restaurant name
    - Exactly 15 menu items
    
    **Example Request:**
    ```json
    {
        "cuisine": "Indian"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "name": "Taj Express",
            "menu": [...]
        },
        "error": null,
        "timestamp": "2025-05-24T10:30:45.123456"
    }
    ```
    """
    try:
        logger.info(f"Received request to generate {request.cuisine} restaurant")
        
        result = service.generate(request.cuisine)
        
        return GenerateRestaurantResponse(
            success=True,
            data=result,
            error=None
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return GenerateRestaurantResponse(
            success=False,
            data=None,
            error=str(e)
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate restaurant: {str(e)}"
        )


@router.post(
    "/generate-batch",
    response_model=BatchGenerateResponse,
    summary="Generate multiple restaurants",
    description="Generate restaurants for multiple cuisine types"
)
async def generate_batch(request: BatchGenerateRestaurantRequest) -> BatchGenerateResponse:
    """
    Generate restaurants for multiple cuisines
    
    **Parameters:**
    - `cuisines`: List of cuisine types (max 10)
    
    **Returns:**
    - List of successfully generated restaurants
    - List of failed generations with errors
    
    **Example Request:**
    ```json
    {
        "cuisines": ["Italian", "Indian", "Japanese"]
    }
    ```
    """
    try:
        logger.info(f"Batch generation requested for {len(request.cuisines)} cuisines")
        
        batch_results = service.generate_batch(request.cuisines)
        
        results = []
        failed = []
        
        for result in batch_results.get("results", []):
            results.append({
                "cuisine": result["cuisine"],
                "restaurant": result["restaurant"]
            })
        
        for fail in batch_results.get("failed", []):
            failed.append({
                "cuisine": fail["cuisine"],
                "error": fail["error"]
            })
        
        return BatchGenerateResponse(
            success=True,
            results=results,
            failed_cuisines=failed if failed else None,
            total_requested=len(request.cuisines),
            total_generated=len(results),
            total_failed=len(failed)
        )
    
    except Exception as e:
        logger.error(f"Batch generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch generation failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if API is running"
)
async def health_check():
    """
    Simple health check endpoint
    
    **Returns:**
    ```json
    {
        "status": "healthy",
        "service": "Restaurant Idea Generator"
    }
    ```
    """
    return {
        "status": "healthy",
        "service": "Restaurant Idea Generator"
    }


@router.get(
    "/examples",
    summary="Get example cuisines",
    description="Get list of example cuisine types that work well"
)
async def get_examples():
    """
    Get example cuisines for testing
    
    **Returns:**
    List of cuisine types that have been tested
    """
    examples = [
        "Indian",
        "Italian",
        "Japanese",
        "Mexican",
        "Thai",
        "French",
        "Chinese",
        "Korean",
        "Spanish",
        "Greek",
        "Turkish",
        "Vietnamese",
        "Lebanese",
        "Portuguese",
        "Peruvian"
    ]
    return {"examples": examples}
