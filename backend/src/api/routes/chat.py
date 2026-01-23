from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from src.api.models.requests import SendMessageRequest
from src.api.models.responses import ChatResponse, ConversationDetailResponse
from src.api.dependencies import get_conversation_service, get_current_user_id
from src.services.conversation.service import ConversationService
from src.core.exceptions import ConversationNotFoundError, LLMError
import json

router = APIRouter()


@router.post("/start", response_model=ConversationDetailResponse)
async def start_conversation(
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Start a new conversation with AI assistant.
    
    Returns:
        ConversationDetailResponse with conversation and initial greeting
    """
    try:
        conversation = conversation_service.start_conversation(user_id)
        messages = conversation_service.get_conversation_history(conversation.id)
        products = conversation_service.get_products_discussed(conversation.id)
        
        return ConversationDetailResponse(
            conversation=conversation,
            messages=messages,
            products_discussed=products
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start conversation: {str(e)}"
        )


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Send a message in a conversation and get AI response.
    
    Args:
        request: Message request with content and optional conversation_id
        
    Returns:
        ChatResponse with user message, assistant response, and related products
    """
    try:
        if request.conversation_id:
            conversation = conversation_service.get_conversation(request.conversation_id)
            
            if conversation.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this conversation"
                )
            conversation_id = request.conversation_id
        else:
            conversation = conversation_service.get_or_start_conversation(user_id)
            conversation_id = conversation.id
        
        result = await conversation_service.send_message(
            conversation_id=conversation_id,
            user_message=request.message
        )
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            user_message=result["user_message"],
            assistant_message=result["assistant_message"],
            products=result.get("products"),
            intent=result.get("intent"),
            stage=result.get("stage")
        )
        
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except LLMError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/message/stream")
async def send_message_stream(
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Send a message and stream the AI response in real-time.
    
    Args:
        request: Message request with content and optional conversation_id
        
    Returns:
        StreamingResponse with Server-Sent Events (SSE)
    """
    try:
        if request.conversation_id:
            conversation = conversation_service.get_conversation(request.conversation_id)
            
            if conversation.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this conversation"
                )
            conversation_id = request.conversation_id
        else:
            conversation = conversation_service.get_or_start_conversation(user_id)
            conversation_id = conversation.id
        
        async def event_generator():
            try:
                stream_result = await conversation_service.send_message_stream(
                    conversation_id=conversation_id,
                    user_message=request.message
                )
                
                async for chunk in stream_result["stream"]:
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                completion_data = {
                    "type": "complete",
                    "conversation_id": stream_result["conversation_id"],
                    "message_id": stream_result["get_assistant_message"]().id,
                    "intent": stream_result.get("intent"),
                    "stage": stream_result.get("stage"),
                    "products": [p.id for p in stream_result.get("products", [])]
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "message": str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Get conversation details with messages and products.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        ConversationDetailResponse with full conversation data
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )
        
        messages = conversation_service.get_conversation_history(conversation_id)
        products = conversation_service.get_products_discussed(conversation_id)
        
        return ConversationDetailResponse(
            conversation=conversation,
            messages=messages,
            products_discussed=products
        )
        
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{conversation_id}/close")
async def close_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Close an active conversation.
    
    Args:
        conversation_id: Conversation ID to close
        
    Returns:
        Success message
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )
        
        conversation_service.close_conversation(conversation_id)
        
        return {"message": "Conversation closed successfully"}
        
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: Conversation ID to delete
        
    Returns:
        Success message
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )
        
        conversation_service.delete_conversation(conversation_id)
        
        return {"message": "Conversation deleted successfully"}
        
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
