from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
import requests
import xml.etree.ElementTree as ET
import datetime
from typing import List, Dict

app = FastAPI()

uri = "bolt://localhost:7687"  
username = "neo4j"             
password = "rootdbms"          
driver = GraphDatabase.driver(uri, auth=(username, password))

def fetch_papers_from_arxiv(topic: str) -> List[Dict]:
    base_url = "http://export.arxiv.org/api/query"
    today = datetime.datetime.now()
    five_years_ago = today - datetime.timedelta(days=5*365)  
    
    published_after = five_years_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    params = {
        "search_query": f"ti:{topic}",
        "start": 0,
        "max_results": 2000,  
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "published_after": published_after,  
    }

    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch data from Arxiv.")
    
    root = ET.fromstring(response.content)
    papers = []
    
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        title = entry.find("{http://www.w3.org/2005/Atom}title").text
        
        if topic.lower() in title.lower():
            paper = {
                "title": title,
                "summary": entry.find("{http://www.w3.org/2005/Atom}summary").text,
                "abstract": entry.find("{http://www.w3.org/2005/Atom}summary").text,  # abstract
                "authors": [author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")],
                "published": entry.find("{http://www.w3.org/2005/Atom}published").text,
                "link": entry.find("{http://www.w3.org/2005/Atom}id").text
            }
            papers.append(paper)
    
    return papers




def delete_existing_data(driver):
    with driver.session() as session:
        session.write_transaction(delete_all_data)

def delete_all_data(tx):
    tx.run("MATCH (p:Paper) DETACH DELETE p")
    tx.run("MATCH (a:Author) DETACH DELETE a")

def add_paper_to_neo4j(driver, paper_data):
    with driver.session() as session:
        session.write_transaction(create_paper_and_authors, paper_data)

def create_paper_and_authors(tx, paper_data):
    # Store paper info including full abstract or text
    tx.run(
        """
        MERGE (p:Paper {title: $title})
        ON CREATE SET p.summary = $summary,
                      p.abstract = $abstract,   // Store the abstract
                      p.published_date = $published_date,
                      p.link = $link
        """,
        title=paper_data["title"],
        summary=paper_data["summary"],
        abstract=paper_data.get("abstract", ""),  # Use abstract or body text
        published_date=paper_data["published"],
        link=paper_data["link"]
    )

    # Add authors
    for author in paper_data["authors"]:
        tx.run(
            """
            MERGE (a:Author {name: $author_name})
            WITH a
            MATCH (p:Paper {title: $title})
            MERGE (a)-[:AUTHORED]->(p)
            """,
            author_name=author,
            title=paper_data["title"]
        )

def summarize_papers_with_ollama():
    with driver.session() as session:
        # Fetch all paper titles and summaries from Neo4j
        query = """
        MATCH (p:Paper)
        RETURN p.title AS title, p.summary AS summary
        """
        result = session.run(query)
        all_text = ""
        for record in result:
            # Combine title and summary for each paper
            all_text += f"Title: {record['title']}\nSummary: {record['summary']}\n\n"

        if not all_text.strip():
            raise HTTPException(status_code=404, detail="No papers found in the database to summarize.")

        # Send the combined text to Ollama for summarization
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "llama2",
            "prompt": f"Summarize the following research developments and suggest future works:\n\n{all_text}"
        }
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to summarize papers using Ollama.")

        result = response.json()
        return result["response"]



@app.get("/search_and_store_papers")
async def search_and_store_papers(topic: str):
    try:
        delete_existing_data(driver)
        
        papers = fetch_papers_from_arxiv(topic)
        
        if not papers:
            raise HTTPException(status_code=404, detail="No papers found for the given topic in the past 5 years.")
        
        for paper in papers:
            add_paper_to_neo4j(driver, paper)
        
        return {"status": "success", "message": f"Fetched and stored {len(papers)} papers for topic '{topic}'."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize_all")
async def summarize_all():
    try:
        summary = summarize_papers_with_ollama()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# def fetch_papers_from_arxiv(topic: str) -> List[Dict]:
#     base_url = "http://export.arxiv.org/api/query"
    
#     today = datetime.datetime.now()
#     five_years_ago = today - datetime.timedelta(days=5*365)  
    
#     published_after = five_years_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
    
#     params = {
#         "search_query": f"ti:{topic}",
#         "start": 0,
#         "max_results": 2000,  
#         "sortBy": "submittedDate",
#         "sortOrder": "descending",
#         "published_after": published_after,  
#     }

#     response = requests.get(base_url, params=params)
    
#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="Failed to fetch data from Arxiv.")
    
#     root = ET.fromstring(response.content)
#     papers = []
    
#     for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
#         title = entry.find("{http://www.w3.org/2005/Atom}title").text
        
#         if topic.lower() in title.lower():
#             paper = {
#                 "title": title,
#                 "summary": entry.find("{http://www.w3.org/2005/Atom}summary").text,
#                 "authors": [author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")],
#                 "published": entry.find("{http://www.w3.org/2005/Atom}published").text,
#                 "link": entry.find("{http://www.w3.org/2005/Atom}id").text
#             }
#             papers.append(paper)
    
#     return papers

# def create_paper_and_authors(tx, paper_data):
#     tx.run(
#         """
#         MERGE (p:Paper {title: $title})
#         ON CREATE SET p.summary = $summary,
#                       p.published_date = $published_date,
#                       p.link = $link
#         """,
#         title=paper_data["title"],
#         summary=paper_data["summary"],
#         published_date=paper_data["published"],
#         link=paper_data["link"]
#     )

#     for author in paper_data["authors"]:
#         tx.run(
#             """
#             MERGE (a:Author {name: $author_name})
#             With a
#             MATCH (p:Paper {title: $title})  // Use MATCH to find the existing Paper node
#             MERGE (a)-[:AUTHORED]->(p)
#             """,
#             author_name=author,
#             title=paper_data["title"]
#         )