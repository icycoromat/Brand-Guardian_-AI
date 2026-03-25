from dotenv import load_dotenv
load_dotenv(override=True)

import uuid
import json
import logging
from pprint import pprint



from backend.src.graph.workflow import app

logging.basicConfig(
    level= logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' 
)
logger = logging.getLogger("brand-guardian-runner")

def run_cli_simulation():
    '''
    Function orchestrate the entire pipline workflow
    -   Creates unique session ID(UNIQUE FIR EVERY SESSION)
    -   Prepares the video url and metadata
    -   Runs it through the AI workflow
    -   Displays the results
    '''
    
    #1: Generating the session ID
    session_id = str(uuid.uuid4())
    logger.info(f"Starting Audit Session: {session_id}")

    #2: Defining Initial State
    initial_inputs = {
        "video_url" : "https://youtu.be/l6v1IWxq35A",
        "video_id" : f"vid_{session_id[:8]}",
        "compliance_results" : [],
        "errors": []
    }

    print("\n--- 1.nput Payload: INITIALIZING WORKFLOW ---")
    print(f"I {json.dumps(initial_inputs, indent=2)}")

    #3: Executing Graph
    try:
        final_state = app.invoke(initial_inputs)

        print("\n--- 2. WORKFLOW EXECUTION COMPLETE ---")
        print("\n=== COMPLIANCE AUDIT REPORT ===")
        print(f"Video ID:    {final_state.get('video_id')}")
        print(f"Status:      {final_state.get('final_status')}")
        print("\n[ VIOLATIONS DETECTED ]")

        results = final_state.get('compliance_results', [])

        if results:
            for issue in results:
                print(f"- [{issue.get('severity')}] {issue.get('category')}: {issue.get('description')}")
        else:
            print("No Voilations Found")
        
        print("\n[Final Summary]")
        print(final_state.get('final_report'))

    except Exception as e:
        logger.error(f"Workflow Execution Failed: {str(e)}")
        raise e


if __name__ == "__main__":
    run_cli_simulation()
