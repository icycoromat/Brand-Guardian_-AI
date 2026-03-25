import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict

#define the compliance issue schema
class ComplianceIssue(TypedDict):
    category: str
    descriptiom: str
    severity: str
    timestamp: Optional[str]


#defining global graph state
class VideoAuditState(TypedDict):
    '''
    defining the data schema for langgraph execution content
    '''
    #input parameters
    video_url: str
    video_id: str

    # ingesting and extracting data
    local_file_path: Optional[str]
    video_metadata: Dict[str,Any]
    transcript: Optional[str]
    ocr_text: List[str]

    #analysis output
    compliance_results: Annotated[List[ComplianceIssue], operator.add]

    #final deliverables
    final_status: str #(Pass|Fail)
    final_report: str #markdown format

    #system observability
    #errors: API timeout, system level errors
    # list if system level crashes
    errors: Annotated[List[str], operator.add]