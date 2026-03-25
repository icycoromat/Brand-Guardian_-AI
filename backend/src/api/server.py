from dotenv import load_dotenv
load_dotenv(override=True) 

import uuid
import logging

#Fast API: Modern web framework like flask but faster
from fastapi import FastAPI, HTTPException

# data validation library(ensire API request have correct format)
from pydantic import BaseModel

from typing import List, Optional


#1: Iinitialize Telemetry 
from backend.src.api.telemetry import setup_telemetry
setup_telemetry()

#2: Import workflow graph
from backend.src.graph.workflow import app as compliance_graph

#3: Setting up Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-server")

#4: Creating FASTapi Application 
app = FastAPI(
    title= "Brand Guardian AI API",
    description= "API for auditing video content against compliance regulations",
    version= "1.0.0"
)

#5: Defining data models(Pydantic)
class AuditRequest(BaseModel):
    '''
    Defines and checks the expected structure of incoming API requests
    '''
    video_url: str

# defines the structure of compliance issue found inside a url
class ComplianceIssue(BaseModel):
    category: str      
    severity: str      
    description: str


class AuditResponse(BaseModel):
    '''
    Defines the structure of API responses:
    
    FastAPI uses this to:
    1. Validate the response before sending (catches bugs)
    2. Auto-generate API documentation (shows users what to expect)
    3. Provide type hints for frontend developers
    
    
    '''
    session_id: str                           
    video_id: str                            
    status: str                               
    final_report: str                         
    compliance_results: List[ComplianceIssue]


#6: Defining main endpoint
@app.post("/audit", response_model=AuditResponse)

async def audit_video(request: AuditRequest):
    """
    Main API endpoint that triggers the compliance audit workflow.
    
    HTTP Method: POST
    URL: http://localhost:8000/audit
    
    Request Body:
    {
        "video_url": "https://youtu.be/abc123"
    }
    
    Response: AuditResponse object (defined above)
    
    Process:
    1. Generate unique session ID
    2. Prepare input for LangGraph workflow
    3. Invoke the graph (Indexer → Auditor)
    4. Return formatted results
    """

    session_id = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"

    logger.info(f"Recieved Audit Request: {request.video_url} (Session: {session_id})")


    #Preparing graph input
    initial_inputs = {
        "video_url": request.video_url,
        "video_id": video_id_short,
        "compliance_results": [],
        "errors": []
    }

    try:
        #Invoking Langgraph workflow
        # ↑ Blocking call - waits for entire workflow to complete
        # ↑ Flow: START → Indexer → Auditor → END
        # ↑ Returns: Final state dictionary with all results
        
        # NOTE: In production, you'd use:
        # await compliance_graph.ainvoke(initial_inputs)
        # ↑ Async version - doesn't block the server while processing
        final_state = compliance_graph.invoke(initial_inputs)

        return AuditResponse(
            session_id= session_id,
            video_id= final_state.get("video_id"),
            status = final_state.get("final_status", "UNKNOWN"),
            final_report= final_state.get("final_report", "No report generated."),
            compliance_results= final_state.get("compliance_results", [])

        )
    except Exception as e:
        logger.error(f"Audit Failed: {e}")

        raise HTTPException(
            status_code= 500,
            detail= f"Workflow Execution Falied: {str(e)}"
        )

#7: Health check endpoint
@app.get("/health")
def health_check():
    """
    Simple endpoint to verify the API is running.
    
    Used by:
    - Load balancers (to check if server is alive)
    - Monitoring systems (uptime checks)
    - Developers (quick test that server started)
    
    Example usage:
    curl http://localhost:8000/health
    
    Response:
    {
        "status": "healthy",
        "service": "Brand Guardian AI"
    }
    """

    return {"status": "healthy", "service": "Brand Guardian AI"}
