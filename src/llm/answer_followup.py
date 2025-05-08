# First define the function
def answer_followup_question(question: str, text: str) -> str:
    """Generate answer to follow-up question using LLM"""
    from openai import OpenAI
    import os
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""
    Based on the following text, answer the question.
    
    TEXT: {text}
    
    QUESTION: {question}
    
    Provide a concise, informative answer based only on information in the text.
    If the text doesn't contain enough information to answer, say so.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"