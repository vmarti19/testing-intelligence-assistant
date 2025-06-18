# Visteon-Assistant-Intelligence (VAI)
Intelligent assistant designed to streamline access to relevant project information and extract specific parameters to optimize the implementation process in automated test cases for generic features.

## Tools

- **Testrack** (Simulation framework)
- **Generic automated test cases** for Indicators and Warnings
- **PGAdmin database**
  - Centralized information.
- **STSS**
- **Messages** (Signals, Network, etc.)
- **MDX** (Applicable VOPS for each program)
- **Warnings and Indicators** (ID, JSON, STSS version)
- **Generic configuration parameters** for input/output features

## Problems

- Interpretation and analysis of feature implementation for automated test cases.
- Fast generation of generic parameter files (`.json`) for each warning or RTT.
- Optimize querying of relevant information in the database.
- Generation of test cases by interpreting pseudocode from JIRA-reported defects.

# Objective

Create an intelligent assistant to streamline access to relevant project information and extract specific parameters to optimize the implementation process in automated test cases for generic features such as warnings and indicators (TTs, RTTs).

# Methodology

## Flow Explanation

1. **Client → Agent**: The user submits a request (e.g., a question or task).
2. **Agent → MCP**: The agent decides how to handle the request and requests access to the model.
3. **MCP → LLM**: The MCP routes the request to the language model (LLM).
4. **LLM → MCP**: The model generates a response and returns it to the MCP.
5. **MCP → Agent**: The MCP delivers the response to the agent.
6. **Agent → Client**: The agent may process, enrich, or contextualize the response before returning it to the user.

---

## Phase I

**Description**: Development of the basic architecture of the intelligent assistant, integrating LLM, Agent, and MCP, with a local console-level client.

**Figure**: Client (LLM): Using a model trained for tools, running on an API such as Ollama or OpenAI.

---

## Phase II

**Description**: Development of tools for the agent, integrating functionalities to execute external tools via MCP.

**Figure**: Model Context Protocol (MCP): Connection to PGAdmin, etc., using `libpsycopg2`, `SQLAlchemy`, etc.

---

## Phase III

**Description**: Integration of the assistant on a remote server.

---

## Phase IV

**Description**: Integration of RAG*, connection to the remote server where RAG will be hosted.  
(*) Reuse of RAG implementation by the DiApps team.

**Figure**: Retrieval-Augmented Generation (RAG): Implementation using frameworks like `langchain` or `llama-index`.

---

## Phase V

**Description**: Development of a client interface integrated into the Testrack webpage for server access. Integrate chatbot interface on the server at `www.testrack.visteon.com`.

