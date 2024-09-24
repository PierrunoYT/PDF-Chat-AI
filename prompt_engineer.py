class PromptEngineer:
    def __init__(self):
        self.system_prompt = """You are an AI assistant tasked with providing accurate and helpful responses based on the given context. 
        Your goal is to synthesize information from the provided context and answer the user's query in a clear and concise manner. 
        If the context doesn't contain enough information to answer the query, say so honestly."""

    def generate_prompt(self, query, context_chunks, conversation_history):
        context = "\n\n".join(chunk for chunk, _ in context_chunks)
        
        conversation = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])
        
        prompt = f"""
        {self.system_prompt}

        Context:
        {context}

        Conversation History:
        {conversation}

        User Query: {query}

        Assistant: Based on the provided context and conversation history, I can answer your query as follows:
        """
        
        return prompt

    def refine_response(self, response, query, context_chunks):
        refinement_prompt = f"""
        Your previous response:
        {response}

        Please review your response and consider the following:
        1. Does it directly address the user's query?
        2. Is it supported by the given context?
        3. Is it concise and clear?

        If necessary, provide a refined response that better addresses these points.

        User Query: {query}

        Refined Response:
        """
        
        # In a real implementation, you would send this refinement_prompt to the AI model
        # and get a refined response. For now, we'll just return the original response.
        return response
