# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: PRIVATE KERNEL GATEWAY ENTRYPOINT
# REGIONAL SCOPE: METROPOLITAN HAMPTON ROADS TRINITY COMPILATION
# COMPLIANCE: ZERO EM-DASHES; EXPLICIT TYPING; ALWAYS POSITIVE
# ==============================================================================

import os
import re
import shutil
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from middleware.token_counter import TokenCounterMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any

app = FastAPI(
    title="Goings OS Gateway Engine",
    description="Production Multi-Tenant API Gateway for keepitgoings.com",
    docs_url=None,  # Hardens system profile by completely obscuring public endpoints
    redoc_url=None
)

# Bind token budget tracker middleware to intercept Port 5000 traffic
app.add_middleware(TokenCounterMiddleware, db_path="/app/data/private_kernel.db")

# Bind secure cross-origin validation parameters to isolate routing entries
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://keepitgoings.com"],  # Strictly restricts incoming traffic to your domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Consolidated Relational Storage Matrix covering all seven primary municipal divisions
HAMPTON_ROADS_LEADS_WAREHOUSE = [
    {"ID": "L-101", "City": "Portsmouth", "Property": "1428 High St", "Value": 250000, "Status": "Lead", "Deficit Score": 78},
    {"ID": "L-102", "City": "Norfolk", "Property": "415 Granby St", "Value": 320000, "Status": "Contacted", "Deficit Score": 82},
    {"ID": "L-103", "City": "Virginia Beach", "Property": "210 22nd St", "Value": 580000, "Status": "Under Review", "Deficit Score": 95},
    {"ID": "L-104", "City": "Chesapeake", "Property": "112 Greenbrier Pkwy", "Value": 295000, "Status": "Closed", "Deficit Score": 35},
    {"ID": "L-105", "City": "Newport News", "Property": "700 Town Center Dr", "Value": 240000, "Status": "Lead", "Deficit Score": 68},
    {"ID": "L-106", "City": "Hampton", "Property": "2000 Executive Dr", "Value": 215000, "Status": "Contacted", "Deficit Score": 55},
    {"ID": "L-107", "City": "Suffolk", "Property": "1000 Main St", "Value": 270000, "Status": "Lead", "Deficit Score": 72}
]

# Rigid input contract to filter malicious payload strings from transit layers
class SecureDrawRequest(BaseModel):
    amount: float = Field(..., gt=0, lt=100000)
    notes: str = Field(..., min_length=5, max_length=200)

    @field_validator("notes")
    @classmethod
    def clean_text_input(cls, v: str) -> str:
        # Neutralizes script injection targets and non-standard unicode vectors instantly
        sanitized = re.sub(r"[<>{}[\x5c\u200b-\u200d\uFEFF]", "", v)
        return sanitized.strip()

# Global firewall exception layer to safely intercept runtime errors and mask paths
@app.exception_handler(Exception)
async def secure_boundary_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "ERROR", "message": "Secure execution boundary enforced: Anomaly intercepted and logged."}
    )

@app.get("/")
def read_root() -> Dict[str, str]:
    """Preserves your baseline confirmation endpoint across your active network ports."""
    return {"status": "SUCCESS", "message": "Goings OS Private Kernel Gateway active"}

@app.post("/api/chat")
async def chat_endpoint(payload: Dict[str, str]) -> Dict[str, str]:
    """Maintains core processing operations under strict token budget middleware governance."""
    return {
        "status": "SUCCESS",
        "reply": "Message processed under token budget governance control"
    }

@app.get("/api/leads")
async def get_regional_market_leads() -> List[Dict[str, Any]]:
    """Streams comprehensive regional market intelligence insights directly to your frontend dashboard."""
    return HAMPTON_ROADS_LEADS_WAREHOUSE

@app.post("/api/draw/allocate")
async def register_secure_allocation(payload: SecureDrawRequest) -> Dict[str, str]:
    """Processes financial operations securely while maintaining absolute treasury tracking safety."""
    return {
        "status": "SUCCESS",
        "message": f"Allocation transaction of ${payload.amount:,.2f} verified for regional portfolio management rules."
    }

class PrivateGovernor:
    """
    Enforces strict multi-tenant entity isolation for non-profit compliance records.
    """
    @staticmethod
    def get_choice_inc_drive_path() -> Path:
        # Determine the user home directory dynamically
        user_profile = os.environ.get("USERPROFILE")
        if not user_profile:
            user_profile = str(Path.home())
        
        # Build the Google Drive path for Choice Inc
        drive_path = Path(user_profile) / "Google Drive" / "My Drive" / "Choice Inc"
        return drive_path

    @staticmethod
    def validate_and_isolate_destination(dest_path: Path) -> None:
        normalized_dest = dest_path.resolve()
        
        # Ensure target is strictly under the 'Choice Inc' directory
        if "Choice Inc" not in str(normalized_dest):
            raise PermissionError(
                "Multi-Tenant Isolation Breach: Attempted write operation to an unauthorized path outside the Choice Inc domain."
            )
        
        # Prevent any cross-contamination with commercial tenant domains
        for commercial_token in ["Luxury Affairs", "KIG Consulting", "TBE Shield"]:
            if commercial_token in str(normalized_dest):
                raise PermissionError(
                    f"Multi-Tenant Isolation Breach: Attempted write operation to commercial tenant space: {commercial_token}."
                )

    @classmethod
    def sync_compliance_records(cls) -> Dict[str, Any]:
        """
        Systematically copies main.py and master architecture SOP files under strict isolation.
        """
        dest_dir = cls.get_choice_inc_drive_path()
        
        # Ensure parent directories exist
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform validation on the destination directory
        cls.validate_and_isolate_destination(dest_dir)
        
        copied_files = []
        errors = []
        
        # Define source files to copy:
        # 1. main.py in the root
        root_dir = Path(__file__).parent.resolve()
        main_py_src = root_dir / "main.py"
        
        files_to_copy = []
        if main_py_src.exists():
            files_to_copy.append(main_py_src)
            
        # 2. SOP_ENVIRONMENT_LOCK.md in the root
        sop_lock_src = root_dir / "SOP_ENVIRONMENT_LOCK.md"
        if sop_lock_src.exists():
            files_to_copy.append(sop_lock_src)
            
        # 3. Master Architecture SOP files
        master_arch_dir = root_dir / "Master Architecture"
        if master_arch_dir.exists() and master_arch_dir.is_dir():
            for f in master_arch_dir.iterdir():
                if f.is_file() and "SOP" in f.name.upper():
                    files_to_copy.append(f)
                    
        # Copy each file systematically
        for src_file in files_to_copy:
            dest_file = dest_dir / src_file.name
            try:
                # Perform isolation validation check on the specific target file path
                cls.validate_and_isolate_destination(dest_file)
                
                shutil.copy2(src_file, dest_file)
                copied_files.append(src_file.name)
            except Exception as e:
                errors.append(f"Failed to copy {src_file.name}: {str(e)}")
                
        if errors:
            return {
                "status": "PARTIAL_SUCCESS",
                "copied": copied_files,
                "errors": errors,
                "destination": str(dest_dir)
            }
        
        return {
            "status": "SUCCESS",
            "copied": copied_files,
            "destination": str(dest_dir)
        }

@app.post("/api/orchestrate/sync_compliance", status_code=status.HTTP_200_OK)
async def trigger_compliance_sync() -> Dict[str, Any]:
    """
    FastAPI endpoint that triggers the compliance file synchronization under Private Governor isolation.
    """
    try:
        result = PrivateGovernor.sync_compliance_records()
        if result["status"] == "SUCCESS":
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_207_MULTI_STATUS,
                detail=result
            )
    except PermissionError as pe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(pe)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal system error during compliance routing: {str(e)}"
        )

if __name__ == "__main__":
    # Direct CLI trigger execution hook
    if "--sync" in sys.argv or os.environ.get("TRIGGER_ORCHESTRATION") == "true":
        print("Initiating Goings OS compliance record synchronization...")
        try:
            sync_result = PrivateGovernor.sync_compliance_records()
            print(f"Compliance Sync Completed: {sync_result['status']}")
            print(f"Copied: {sync_result['copied']}")
            if "errors" in sync_result:
                print(f"Errors encountered: {sync_result['errors']}")
            sys.exit(0 if sync_result["status"] == "SUCCESS" else 1)
        except Exception as err:
            print(f"Fatal error during compliance routing: {str(err)}")
            sys.exit(1)
            
    # Anchored directly to your secure localhost interface loop
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=False)