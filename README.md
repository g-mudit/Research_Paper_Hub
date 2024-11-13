# Research Paper Hub

**Research Paper Hub** is a platform designed to fetch, store, and display research papers from the ArXiv repository. It provides an interface for users to search for papers by topic, view detailed information, and access the full paper via a link to ArXiv. 

The project is composed of two main components:

- **Backend (FastAPI)**: Fetches research papers from ArXiv, stores them in a Neo4j graph database, and serves them via an API.
- **Frontend (Streamlit)**: A simple UI that allows users to search for papers by topic and view detailed information, including abstract and authors.

---

## Features

### **Backend (FastAPI)**

- **Fetch Papers from ArXiv**: The backend queries the ArXiv API to fetch research papers published in the last 5 years based on a user-defined topic.
  
- **Store Papers in Neo4j**: Once fetched, the papers are stored in a Neo4j graph database with relationships to authors.

- **Search Papers**: The backend allows searching for papers by topic, and returns results sorted by the date of publication.

### **Frontend (Streamlit)**

- **Search Papers**: Users can input a topic (e.g., "Artificial Intelligence") and fetch research papers related to the topic from the Neo4j database.

- **View Paper Details**: Each paper's details are displayed, including title, abstract, authors, and publication date. Links to the full papers on ArXiv are also provided.

---

## Installation

### **1. Clone the Repository**

Clone the repository to your local machine using:

```bash
git clone https://github.com/g-mudit/Research_Paper_Hub.git
```

### **2. Installing required packages**
Install required packages from requirements.txt
```cmd
pip install -r requirements.txt
```
### **3. Run streamlit file**
```bash
streamlit run streamlit_app.py
```
### **4. Note : Install Neo4j and give credentialls for database**
