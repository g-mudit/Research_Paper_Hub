import subprocess
import threading
import requests
import time
import streamlit as st
from neo4j import GraphDatabase

# Neo4j credentials
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "rootdbms")

# Start FastAPI as a subprocess
def start_fastapi():
    subprocess.run(["uvicorn", "store_papers:app", "--host", "0.0.0.0", "--port", "8000"])

# Run FastAPI in a background thread
threading.Thread(target=start_fastapi, daemon=True).start()

# Allow FastAPI to start
time.sleep(5)

# Function to fetch papers from Neo4j
driver = GraphDatabase.driver(URI, auth=AUTH)

def get_papers_from_neo4j():
    with driver.session() as session:
        query = """
        MATCH (a:Author)-[:AUTHORED]->(p:Paper)
        RETURN p.title AS title, p.summary AS summary, p.published_date AS published, p.link AS link, collect(a.name) AS authors
        ORDER BY p.published_date DESC
        """
        result = session.run(query)
        papers = []
        for record in result:
            papers.append({
                "title": record["title"],
                "summary": record["summary"],
                "published": record["published"],
                "link": record["link"],
                "authors": ", ".join(record["authors"]),
            })
        return papers

# Streamlit interface
st.title("Research Papers Search and Display")

topic = st.text_input("Enter a topic to search for research papers:")

FASTAPI_ENDPOINT = "http://127.0.0.1:8000/search_and_store_papers"

if st.button("Fetch Papers"):
    if topic:
        with st.spinner(f"Fetching papers on '{topic}'..."):
            response = requests.get(f"{FASTAPI_ENDPOINT}?topic={topic}")
            
            if response.status_code == 200:
                st.success(f"Papers on '{topic}' have been successfully fetched.")
            else:
                st.error(f"Error fetching papers: {response.json().get('detail', 'Unknown error')}")
    else:
        st.warning("Please enter a topic before fetching papers.")

st.write("---")
st.header("Fetched Research Papers")

papers = get_papers_from_neo4j()

if papers:
    for paper in papers:
        with st.expander(paper['title']):  
            st.write(f"**Authors**: {paper['authors']}")
            st.write(f"**Published on**: {paper['published']}")
            st.write(paper['summary'])
            st.markdown(f"[Read Full Paper]({paper['link']})")
else:
    st.write("No papers found in the database.")

st.write("---")
st.header("Summarize All Papers")

if st.button("Summarize All"):
    with st.spinner("Summarizing all research papers..."):
        try:
            summary_response = requests.post("http://127.0.0.1:8000/summarize_all")
            if summary_response.status_code == 200:
                st.success("Summarization complete!")
                st.write(summary_response.json().get("summary", "No summary available."))
            else:
                st.error("Failed to summarize papers. Please check the backend logs.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


# import streamlit as st
# import requests
# from neo4j import GraphDatabase

# URI = "bolt://localhost:7687"  
# AUTH = ("neo4j", "rootdbms")   

# FASTAPI_ENDPOINT = "http://127.0.0.1:8000/search_and_store_papers"

# driver = GraphDatabase.driver(URI, auth=AUTH)

# def get_papers_from_neo4j():
#     with driver.session() as session:
#         query = """
#         MATCH (a:Author)-[:AUTHORED]->(p:Paper)
#         RETURN p.title AS title, p.summary AS summary, p.published_date AS published, p.link AS link, collect(a.name) AS authors
#         ORDER BY p.published_date DESC
#         """
#         result = session.run(query)
#         papers = []
#         for record in result:
#             papers.append({
#                 "title": record["title"],
#                 "summary": record["summary"],
#                 "published": record["published"],
#                 "link": record["link"],
#                 "authors": ", ".join(record["authors"]),
#             })
#         return papers

# st.title("Research Papers Search and Display")

# topic = st.text_input("Enter a topic to search for research papers:")

# if st.button("Fetch Papers"):
#     if topic:
#         with st.spinner(f"Fetching papers on '{topic}'..."):
#             response = requests.get(f"{FASTAPI_ENDPOINT}?topic={topic}")
            
#             if response.status_code == 200:
#                 st.success(f"Papers on '{topic}' in  past 5 years, have been successfully fetched ")
#             else:
#                 st.error(f"Error fetching papers: {response.json().get('detail', 'Unknown error')}")
#     else:
#         st.warning("Please enter a topic before fetching papers.")

# st.write("---")
# st.header("Fetched Research Papers")

# papers = get_papers_from_neo4j()

# if papers:
#     for paper in papers:
#         with st.expander(paper['title']):  
#             st.write(f"**Authors**: {paper['authors']}")
#             st.write(f"**Published on**: {paper['published']}")
#             st.write(paper['summary'])
#             st.markdown(f"[Read Full Paper]({paper['link']})")
# else:
#     st.write("No papers found in the database.")

# st.write("---")
# st.header("Summarize All Papers")

# if st.button("Summarize All"):
#     with st.spinner("Summarizing all research papers..."):
#         try:
#             summary_response = requests.post("http://127.0.0.1:8000/summarize_all")
#             if summary_response.status_code == 200:
#                 st.success("Summarization complete!")
#                 st.write(summary_response.json().get("summary", "No summary available."))
#             else:
#                 st.error("Failed to summarize papers. Please check the backend logs.")
#         except Exception as e:
#             st.error(f"An error occurred: {e}")


