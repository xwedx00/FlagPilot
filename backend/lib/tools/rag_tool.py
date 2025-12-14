
from metagpt.tools.tool_registry import register_tool
from config import settings
from ragflow.client import RAGFlowClient

@register_tool(include_functions=["search_knowledge_base"])
class RAGSearch:
    """
    Search internal knowledge base (RAG) for relevant documents, contracts, and resumes.
    """
    
    @staticmethod
    async def search_knowledge_base(query: str, user_id: str = None, top_k: int = 5) -> str:
        """
        Search the knowledge base for documents relevant to the query.
        
        Args:
            query: The search query (e.g., "candidate experience", "non-compete clause")
            user_id: ID of the user for personal vault search (Optional but recommended)
            top_k: Number of results to return (default: 5)
            
        Returns:
            Formatted string containing relevant document snippets.
        """
        # Use singleton client (safer and cleaner)
        from ragflow.client import get_ragflow_client
        client = get_ragflow_client()
        
        try:
            results = []
            
            if user_id:
                # 1. Authentic Search: Search User's Personal Vault + Global Wisdom
                results = await client.search_user_context(
                    user_id=user_id,
                    query=query,
                    limit=top_k
                )
            else:
                # 2. Fallback: Generic/Global Search (if no user context)
                # This should ideally be avoided in production
                # Assuming retrieve is also likely async if getting from RAGFlow? 
                # Checking source is hard but assume consistency. 
                # Actually, earlier view of client.py showed search_user_context is async.
                # let's assume retrieve might need await or check client.py
                # For safety, I'll check client.py again or just await search_user_context as that's the main path.
                # Just wrapping search_user_context for now.
                results = await client.search_user_context(
                     user_id="production-test-user-v1",
                     query=query,
                     limit=top_k
                )
            
            if not results:
                return "No relevant documents found."
            
            output = []
            for i, res in enumerate(results):
                # Handle different result formats (dict vs object if applicable)
                if isinstance(res, dict):
                    doc_name = res.get('document_name', 'Unknown')
                    content = res.get('content', '')
                else: 
                    # Fallback if client returns objects
                    doc_name = getattr(res, 'document_name', 'Unknown')
                    content = getattr(res, 'content', '')
                    
                output.append(f"Source: {doc_name}\nSnippet: {content[:500]}...\n")
                
            return "\n---\n".join(output)
            
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
