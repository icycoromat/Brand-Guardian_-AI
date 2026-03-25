#Azure OpenTelemetry integration

import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor


# Creating a telemetry logger
logger = logging.getLogger("brand-guardian-telemetry")

def setup_telemetry():
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.warning("No Instrument key foun, Telemetry is DISABLED")
        return 
    
    try:
        #Register automatic instrument for:
        #-   http requests
        #-  Database calls
        #-  Seeing detailed metrics about api(can see which part of api ins slow)
        
        configure_azure_monitor(
            connection_string=connection_string,  
            logger_name="brand-guardian-tracer"
        )
        logger.info("Azure Monitor Tracking Enabled & Connected")

    except Exception as e:
        logger.error(f"Failed to connect to Azure Monitor: {e}")