from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.api.models.responses import (
    ConversationListResponse,
    ConversationDetailResponse,
    MessageListResponse,
    ConversationSummaryResponse
)
from src.api.dependencies import get_conversation_service, get_current_user_id
from src.services.conversation.service import ConversationService
from src.core.exceptions import ConversationNotFoundError

router = APIRouter()


@router.get("/conversations", response_model=ConversationListResponse)
async def get_user_conversations(
    limit: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Get all conversations for the current user.
    
    Args:
        limit: Maximum number of conversations to return
        
    Returns:
        ConversationListResponse with user's conversations
    """
    conversations = conversation_service.get_user_conversations(user_id, limit)
    
    return ConversationListResponse(
        conversations=conversations,
        total=len(conversations)
    )


@router.get("/active", response_model=ConversationDetailResponse)
async def get_active_conversation(
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Get the current active conversation for the user.
    
    Returns:
        ConversationDetailResponse if active conversation exists
        
    Raises:
        404: If no active conversation exists
    """
    conversation = conversation_service.get_active_conversation(user_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation found"
        )
    
    messages = conversation_service.get_conversation_history(conversation.id)
    products = conversation_service.get_products_discussed(conversation.id)
    
    return ConversationDetailResponse(
        conversation=conversation,
        messages=messages,
        products_discussed=products
    )


@router.get("/conversations/active", response_model=ConversationDetailResponse)
async def get_active_conversation_alt(
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Get the current active conversation for the user (alternative path).
    
    This is an alias for /active for backward compatibility.
    
    Returns:
        ConversationDetailResponse if active conversation exists
        
    Raises:
        404: If no active conversation exists
    """
    return await get_active_conversation(user_id, conversation_service)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_detail(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Get detailed information about a specific conversation.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        ConversationDetailResponse with full conversation data
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        # Verify ownership
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


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Get messages from a specific conversation with pagination.
    
    Args:
        conversation_id: Conversation ID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        
    Returns:
        MessageListResponse with conversation messages
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )
        
        messages = conversation_service.get_conversation_history(
            conversation_id,
            limit=limit
        )
        
        return MessageListResponse(
            messages=messages,
            total=len(messages),
            conversation_id=conversation_id
        )
        
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/conversations/{conversation_id}/summary", response_model=ConversationSummaryResponse)
async def get_conversation_summary(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Get a summary of a conversation including statistics and insights.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        ConversationSummaryResponse with conversation analytics
    """
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation"
            )
        
        summary = conversation_service.get_conversation_summary(conversation_id)
        
        return ConversationSummaryResponse(**summary)
        
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
