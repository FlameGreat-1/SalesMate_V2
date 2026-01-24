from typing import Dict, Any, Optional, List, Callable

from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.repositories.user import UserRepository
from src.repositories.profile import ProfileRepository
from src.services.conversation.session_manager import SessionManager
from src.services.llm.service import LLMService
from src.services.product.service import ProductService
from src.services.user.service import UserService
from src.core.schemas.conversation import ConversationResponse
from src.core.schemas.message import MessageResponse
from src.core.schemas.user import UserResponse
from src.core.schemas.profile import ProfileResponse
from src.core.schemas.product import ProductResponse
from src.core.schemas.product import ProductFilter
from src.core.models.enums import UserIntent
from src.core.exceptions import ConversationNotFoundError, LLMError
from src.config import settings

from src.utils.logger import get_logger
logger = get_logger(__name__)


class ConversationService:
    def __init__(self):
        self.session_manager = SessionManager()
        self.llm_service = LLMService()
        self.product_service = ProductService()
        self.user_service = UserService()
    
    def start_conversation(self, user_id: str) -> ConversationResponse:
        conversation = self.session_manager.create_session(user_id)
        
        try:
            greeting = self.llm_service.generate_greeting(user_id)
            
            self.session_manager.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=greeting,
                intent=UserIntent.GREETING.value
            )
            
            self.session_manager.update_session_stage(conversation.id, "greeting")
            
        except Exception as e:
            logger.error(f"Failed to generate greeting: {str(e)}")
            default_greeting = "Hello! I'm here to help you find the perfect electronics. What are you looking for today?"
            self.session_manager.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=default_greeting,
                intent=UserIntent.GREETING.value
            )
        
        return self.session_manager.get_session(conversation.id)
    
    async def send_message(
        self,
        conversation_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        conversation = self.session_manager.get_session(conversation_id)
        
        user_msg = self.session_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        
        try:
            conversation_history = self._prepare_messages_for_llm(conversation_id)
            
            intent_data = self.llm_service.analyze_intent(
                user_message=user_message,
                conversation_history=conversation_history
            )
            
            self.session_manager.add_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                intent=intent_data["intent"].value,
                metadata={"intent_analysis": intent_data}
            )
            
            products = self._get_relevant_products(
                conversation_id=conversation_id,
                user_message=user_message,
                intent_data=intent_data
            )
            
            full_catalog = self.product_service.get_all_products()
            
            messages = self._prepare_messages_for_llm(conversation_id)
            
            stage = self._determine_conversation_stage(intent_data["intent"])
            
            response = await self.llm_service.generate_response(
                user_id=conversation.user_id,
                messages=messages,
                available_products=products,
                full_catalog=full_catalog,
                conversation_stage=stage,
                stream=False
            )
            
            assistant_msg = self.session_manager.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response,
                metadata={
                    "products_shown": [p.id for p in products] if products else [],
                    "stage": stage
                }
            )
            
            self.session_manager.update_session_stage(conversation_id, stage)
            
            if products:
                for product in products:
                    self.session_manager.add_product_to_session(conversation_id, product.id)
            
            return {
                "conversation_id": conversation_id,
                "user_message": user_msg,
                "assistant_message": assistant_msg,
                "intent": intent_data["intent"].value,
                "products": products,
                "stage": stage
            }
            
        except LLMError as e:
            logger.error(f"LLM error in conversation {conversation_id}: {str(e)}")
            error_response = "I apologize, but I'm having trouble processing your request right now. Please try again."
            
            assistant_msg = self.session_manager.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=error_response,
                metadata={"error": str(e)}
            )
            
            return {
                "conversation_id": conversation_id,
                "user_message": user_msg,
                "assistant_message": assistant_msg,
                "error": str(e)
            }
    
    async def send_message_stream(
        self,
        conversation_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        conversation = self.session_manager.get_session(conversation_id)
        
        user_msg = self.session_manager.add_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        
        try:
            conversation_history = self._prepare_messages_for_llm(conversation_id)
            
            intent_data = self.llm_service.analyze_intent(
                user_message=user_message,
                conversation_history=conversation_history
            )
            
            products = self._get_relevant_products(
                conversation_id=conversation_id,
                user_message=user_message,
                intent_data=intent_data
            )
            
            full_catalog = self.product_service.get_all_products()
            messages = self._prepare_messages_for_llm(conversation_id)
            stage = self._determine_conversation_stage(intent_data["intent"])
            
            stream = await self.llm_service.generate_response(
                user_id=conversation.user_id,
                messages=messages,
                available_products=products,
                full_catalog=full_catalog,
                conversation_stage=stage,
                stream=True
            )
            
            assistant_msg_container = {"message": None}
            
            async def stream_and_save():
                full_response = []
                async for chunk in stream:
                    full_response.append(chunk)
                    yield chunk
                
                complete_response = "".join(full_response)
                
                assistant_msg = self.session_manager.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=complete_response,
                    metadata={
                        "products_shown": [p.id for p in products] if products else [],
                        "stage": stage
                    }
                )
                
                assistant_msg_container["message"] = assistant_msg
                
                self.session_manager.update_session_stage(conversation_id, stage)
                
                if products:
                    for product in products:
                        self.session_manager.add_product_to_session(conversation_id, product.id)
            
            return {
                "stream": stream_and_save(),
                "conversation_id": conversation_id,
                "user_message": user_msg,
                "intent": intent_data["intent"].value,
                "products": products,
                "stage": stage,
                "get_assistant_message": lambda: assistant_msg_container["message"]
            }
            
        except LLMError as e:
            logger.error(f"LLM error in conversation {conversation_id}: {str(e)}")
            raise
    
    def _get_relevant_products(
        self,
        conversation_id: str,
        user_message: str,
        intent_data: Dict[str, Any]
    ) -> List[ProductResponse]:
        conversation = self.session_manager.get_session(conversation_id)
        profile = self.user_service.get_user_profile(conversation.user_id)
        
        products: List[ProductResponse] = []
        product_ids_added: set = set()
        
        def add_products(new_products: List[ProductResponse]):
            for p in new_products:
                if p.id not in product_ids_added:
                    products.append(p)
                    product_ids_added.add(p.id)
        
        mentioned_products = intent_data.get("products", [])
        if mentioned_products:
            for product_name in mentioned_products:
                found = self.product_service.search_products(
                    query=product_name,
                    filters=ProductFilter(limit=3)
                )
                add_products(found)
        
        if intent_data["intent"] == UserIntent.ASKING_QUESTION:
            if conversation.products_discussed:
                discussed = self.product_service.get_products_by_ids(
                    conversation.products_discussed
                )
                add_products(discussed)
        
        if products:
            return products
        
        if intent_data["intent"] == UserIntent.REQUESTING_RECOMMENDATION:
            found = self.product_service.search_products(
                query=user_message,
                profile=profile,
                filters=ProductFilter(limit=5)
            )
            add_products(found)
        
        elif intent_data["intent"] in [UserIntent.BROWSING, UserIntent.ASKING_QUESTION]:
            if intent_data.get("categories"):
                category = intent_data["categories"][0]
                found = self.product_service.get_products_by_category(category, limit=10)
            else:
                found = self.product_service.search_products(
                    query=user_message,
                    profile=profile,
                    filters=ProductFilter(limit=10)
                )
            add_products(found)
        
        elif intent_data["intent"] == UserIntent.COMPARING_PRODUCTS:
            found = self.product_service.search_products(
                query=user_message,
                profile=profile,
                filters=ProductFilter(limit=5)
            )
            add_products(found)
        
        if not products and conversation.products_discussed:
            discussed = self.product_service.get_products_by_ids(
                conversation.products_discussed
            )
            add_products(discussed)
        
        return products
    
    def _prepare_messages_for_llm(self, conversation_id: str) -> List[Dict[str, str]]:
        messages = self.session_manager.get_recent_messages(
            conversation_id,
            limit=settings.conversation.context_window_messages
        )
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return formatted_messages
    
    def _determine_conversation_stage(self, intent: UserIntent) -> str:
        stage_mapping = {
            UserIntent.GREETING: "greeting",
            UserIntent.BROWSING: "discovery",
            UserIntent.REQUESTING_RECOMMENDATION: "recommendation",
            UserIntent.COMPARING_PRODUCTS: "comparison",
            UserIntent.ASKING_QUESTION: "discovery",
            UserIntent.READY_TO_BUY: "closing",
            UserIntent.OBJECTION: "objection_handling",
            UserIntent.UNKNOWN: "discovery"
        }
        return stage_mapping.get(intent, "discovery")
    
    def get_conversation(self, conversation_id: str) -> ConversationResponse:
        return self.session_manager.get_session(conversation_id)
    
    def get_conversation_with_messages(
        self,
        conversation_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        conversation = self.session_manager.get_session(conversation_id)
        messages = self.session_manager.get_session_messages(conversation_id, limit)
        
        return {
            "conversation": conversation,
            "messages": messages,
            "message_count": len(messages)
        }
    
    def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[ConversationResponse]:
        return self.session_manager.get_user_sessions(user_id, limit)
    
    def get_active_conversation(self, user_id: str) -> Optional[ConversationResponse]:
        return self.session_manager.get_active_session(user_id)
    
    def get_or_start_conversation(self, user_id: str) -> ConversationResponse:
        active_conversation = self.get_active_conversation(user_id)
        if active_conversation:
            return active_conversation
        return self.start_conversation(user_id)
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 100
    ) -> List[MessageResponse]:
        return self.session_manager.get_session_messages(conversation_id, limit)
    
    def get_products_discussed(self, conversation_id: str) -> List[ProductResponse]:
        conversation = self.session_manager.get_session(conversation_id)
        
        if not conversation.products_discussed:
            return []
        
        return self.product_service.get_products_by_ids(conversation.products_discussed)
    
    def recommend_products(
        self,
        conversation_id: str,
        limit: int = 5
    ) -> List[ProductResponse]:
        conversation = self.session_manager.get_session(conversation_id)
        profile = self.user_service.get_user_profile(conversation.user_id)
        
        if profile:
            return self.product_service.get_recommendations_for_user(profile, limit)
        
        messages = self.session_manager.get_recent_messages(conversation_id, limit=10)
        user_messages = [m for m in messages if m.role == "user"]
        
        if user_messages:
            last_message = user_messages[-1].content
            return self.product_service.search_products(
                query=last_message,
                filters=ProductFilter(limit=limit)
            )
        
        return []
    
    def get_similar_products(
        self,
        conversation_id: str,
        product_id: str,
        limit: int = 3
    ) -> List[ProductResponse]:
        return self.product_service.get_similar_products(product_id, limit)
    
    def close_conversation(self, conversation_id: str) -> ConversationResponse:
        return self.session_manager.close_session(conversation_id)
    
    def abandon_conversation(self, conversation_id: str) -> ConversationResponse:
        return self.session_manager.abandon_session(conversation_id)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        return self.session_manager.delete_session(conversation_id)
    
    def update_conversation_context(
        self,
        conversation_id: str,
        context: Dict[str, Any]
    ) -> ConversationResponse:
        return self.session_manager.update_session_context(conversation_id, context)
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        conversation = self.session_manager.get_session(conversation_id)
        messages = self.session_manager.get_session_messages(conversation_id)
        products = self.get_products_discussed(conversation_id)
        
        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]
        
        intents = {}
        for msg in messages:
            if msg.intent:
                intents[msg.intent] = intents.get(msg.intent, 0) + 1
        
        return {
            "conversation_id": conversation.id,
            "user_id": conversation.user_id,
            "status": conversation.status,
            "stage": conversation.stage,
            "started_at": conversation.created_at,
            "last_activity": conversation.updated_at,
            "message_count": len(messages),
            "user_message_count": len(user_messages),
            "assistant_message_count": len(assistant_messages),
            "products_discussed_count": len(products),
            "products_discussed": [p.name for p in products],
            "intents": intents,
            "context": conversation.context
        }
    
    async def regenerate_response(
        self,
        conversation_id: str
    ) -> MessageResponse:
        messages = self.session_manager.get_recent_messages(conversation_id, limit=2)
        
        if not messages or messages[-1].role != "assistant":
            raise ValueError("No assistant message to regenerate")
        
        user_messages = [m for m in messages if m.role == "user"]
        if not user_messages:
            raise ValueError("No user message found")
        
        last_user_message = user_messages[-1].content
        
        conversation = self.session_manager.get_session(conversation_id)
        
        conversation_history = self._prepare_messages_for_llm(conversation_id)
        conversation_history = conversation_history[:-1]
        
        intent_data = self.llm_service.analyze_intent(
            user_message=last_user_message,
            conversation_history=conversation_history
        )
        
        products = self._get_relevant_products(
            conversation_id=conversation_id,
            user_message=last_user_message,
            intent_data=intent_data
        )
        
        full_catalog = self.product_service.get_all_products()
        
        llm_messages = self._prepare_messages_for_llm(conversation_id)
        llm_messages = llm_messages[:-1]
        
        stage = self._determine_conversation_stage(intent_data["intent"])
        
        response = await self.llm_service.generate_response(
            user_id=conversation.user_id,
            messages=llm_messages,
            available_products=products,
            full_catalog=full_catalog,
            conversation_stage=stage,
            stream=False
        )
        
        assistant_msg = self.session_manager.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response,
            metadata={
                "regenerated": True,
                "products_shown": [p.id for p in products] if products else [],
                "stage": stage
            }
        )
        
        return assistant_msg


def get_conversation_service() -> ConversationService:
    return ConversationService()
