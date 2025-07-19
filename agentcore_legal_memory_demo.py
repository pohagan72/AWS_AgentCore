```python
# Import necessary libraries
import time
from bedrock_agentcore.memory import MemoryClient

# 1. SETUP: Create a persistent memory store for a specific case
# This acts as the AI Agent's long-term "case file".

memory_client = MemoryClient(region_name="us-east-1")
case_file_memory_name = "Case_File_ProjectX_Depositions"
attorney_id = "attorney_jane_doe"

print(f"Creating long-term memory for: {case_file_memory_name}...")
case_memory = memory_client.create_memory_and_wait(
    name=case_file_memory_name,
    description="Long-term memory for eDiscovery and case facts for Project X.",
    strategies=[{
        "semanticMemoryStrategy": {
            "name": "CaseFactExtractor",
            # Namespaces organize facts, here by the attorney on the case
            "namespaces": [f"/case_facts/{attorney_id}"]
        }
    }]
)
case_memory_id = case_memory.get("id")
print("Memory store created successfully.")


# 2. INGESTION: The agent processes depositions as they become available
def analyze_and_store_deposition_facts(session_id, transcript_summary):
    """Simulates an AI agent processing a deposition and storing key facts."""
    print(f"\nAnalyzing deposition for session: {session_id}...")
    memory_client.create_event(
        memory_id=case_memory_id,
        actor_id=attorney_id,
        session_id=session_id,
        messages=[(transcript_summary, "DEPOSITION_SUMMARY")]
    )
    print(f"Key fact stored: '{transcript_summary}'")

# Analyze the first deposition transcript
deposition_1_summary = "In John Smith's deposition, he confirmed receiving the memo about 'Project X' component failures on May 1st, 2024."
analyze_and_store_deposition_facts("deposition_session_01", deposition_1_summary)

# Simulate time passing before the next deposition. In a real-world scenario,
# this could be weeks. The agent's memory persists.
print("\n... time passes, long-term memory is processed by AWS ...")

# Analyze a second, related deposition
deposition_2_summary = "Jane Doe's deposition reveals she sent the 'Project X' component failure memo to John Smith and followed up via email."
analyze_and_store_deposition_facts("deposition_session_02", deposition_2_summary)


# 3. RETRIEVAL: Weeks later, the attorney can query the agent's memory
def ask_agent_about_case(query):
    """Simulates an attorney asking the agent a natural language question about the case."""
    print(f"\nQuerying the case file: '{query}'")
    retrieved_memories = memory_client.retrieve_memories(
        memory_id=case_memory_id,
        namespace=f"/case_facts/{attorney_id}",
        query=query
    )
    
    # The response contains a list of relevant memories with scores
    print("\n--- Agent's Recollection ---")
    if retrieved_memories.get('memoryRecords'):
        for record in retrieved_memories['memoryRecords']:
            # The actual fact is nested in the payload
            print(f"- {record['payload']['string']}")
    else:
        print("No specific facts found for that query.")
    print("--------------------------")

# The attorney asks a high-level question, relying on the agent's accumulated knowledge
attorney_query = "What evidence shows John Smith knew about the component failures?"
ask_agent_about_case(attorney_query)

