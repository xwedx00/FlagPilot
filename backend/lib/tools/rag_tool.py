
from metagpt.tools.tool_registry import register_tool
from config import settings
from ragflow.client import RAGFlowClient

@register_tool(include_functions=["search_knowledge_base"])
class RAGSearch:
    """
    Search internal knowledge base (RAG) for relevant documents, contracts, and resumes.
    """
    
    @staticmethod
    def search_knowledge_base(query: str, top_k: int = 5) -> str:
        """
        Search the knowledge base for documents relevant to the query.
        
        Args:
            query: The search query (e.g., "candidate experience", "non-compete clause")
            top_k: Number of results to return (default: 5)
            
        Returns:
            Formatted string containing relevant document snippets.
        """
        client = RAGFlowClient(
            base_url=settings.RAGFLOW_URL,
            api_key=settings.RAGFLOW_API_KEY
        )
        
        # Determine dataset (Personal + Global logic handled by client)
        # For now, we search generally. In a real user session, we'd need user_id context.
        # This basic tool assumes general context or relies on client defaults.
        
        try:
            results = client.retrieve(
                dataset_name="production-test-user-v1", # Default for now, can be dynamic
                query=query,
                top_k=top_k
            )
            
            if not results:
                return "No relevant documents found."
            
            output = []
            for i, res in enumerate(results):
                output.append(f"Source: {res.get('document_name', 'Unknown')}\nSnippet: {res.get('content', '')[:500]}...\n")
                
            return "\n---\n".join(output)
            
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
