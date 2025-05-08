import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def extract_news_content(url):
    """
    Extract the main content from a news article URL.
    
    Args:
        url (str): The URL of the news article.
        
    Returns:
        str: The main text content of the article with boilerplate removed.
    """
    # Send HTTP request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching the article: {e}"
    
    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove unwanted elements
    for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
        element.decompose()
        
    # Remove ads and other non-content elements
    for div in soup.find_all('div', class_=re.compile(r'ad|banner|promo|sidebar|comment|footer|menu|nav|related|social|share', re.I)):
        div.decompose()
    
    # Try to find the main article content
    article_content = None
    
    # Common article containers
    potential_content_elements = [
        soup.find('article'),
        soup.find('div', class_=re.compile(r'article|post|content|entry|body', re.I)),
        soup.find('div', id=re.compile(r'article|post|content|entry|body', re.I)),
        soup.find('main')
    ]
    
    # Use the first valid content container found
    for element in potential_content_elements:
        if element:
            article_content = element
            break
    
    # If no specific content container is found, use the body
    if not article_content:
        article_content = soup.find('body')
    
    # Extract paragraphs from the content
    if article_content:
        paragraphs = article_content.find_all('p')
        content = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 40])
        
        # If no substantial paragraphs are found, try to get text directly
        if not content:
            content = article_content.get_text(separator='\n\n').strip()
            
        # Clean up the content
        content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
        content = re.sub(r'\s{2,}', ' ', content)     # Remove excessive whitespace
        
        return content
    
    return "Could not extract article content from the provided URL."


if __name__ == "__main__":
    # Example usage
    url = input("Enter the news article URL: ")
    article_text = extract_news_content(url)
    print(article_text)