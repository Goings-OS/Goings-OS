import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.topics',
    'https://www.googleapis.com/auth/classroom.rosters'
]

def deploy_3tier_enterprise_classroom():
    print("============================================================")
    print("   GOINGS OS ACADEMY: $1M ENTERPRISE CLASSROOM DEPLOYMENT    ")
    print("============================================================")
    
    creds = None
    token_path = 'token.json'
    creds_path = 'goings-os-academy/credentials.json'

    # Remove any old or invalid cached token
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            os.remove(token_path)
            creds = None
        
    if not creds or not creds.valid:
        if not os.path.exists(creds_path):
            print(f"[ERROR] Missing {creds_path}.")
            return
            
        # Read credential file and ensure desktop application structure
        with open(creds_path, 'r') as f:
            client_config = json.load(f)
            
        if 'web' in client_config:
            client_config['installed'] = client_config.pop('web')
            
        if 'installed' in client_config:
            client_config['installed']['redirect_uris'] = ['http://localhost:8080/', 'http://localhost']

        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        
        print("\n[AUTH] Opening browser for Google authorization on port 8080...")
        creds = flow.run_local_server(host='localhost', port=8080, prompt='consent')
        
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    service = build('classroom', 'v1', credentials=creds)
    
    try:
        course_body = {
            'name': 'Goings OS Academy: Sovereign Enterprise Track',
            'section': 'Cohort 001 (3-Tier Master Class)',
            'descriptionHeading': 'The Goings OS Operational Standard',
            'description': '3-Tier pathways for Novice Beginners, Intermediate Operators, and System Architects.',
            'room': 'Command Bridge',
            'ownerId': 'me',
            'courseState': 'ACTIVE'
        }
        
        course = service.courses().create(body=course_body).execute()
        course_id = course.get('id')
        print(f"\n[SUCCESS] Course Created! ID: {course_id}")
        print(f"[LINK] Classroom URL: {course.get('alternateLink')}\n")

        topics = [
            '00. START HERE // System Rules & Student FAQs',
            'TIER 1 // Novice Foundations & C-P-O Prompting',
            'TIER 2 // Practitioner Automation & Speed-to-Lead',
            'TIER 3 // Architect Microservices & Private Governor'
        ]
        
        for topic_name in topics:
            topic_body = {'name': topic_name}
            service.courses().topics().create(courseId=course_id, body=topic_body).execute()
            print(f"[TOPIC CREATED] {topic_name}")

        print("\n============================================================")
        print("   CLASSROOM DEPLOYED SUCCESSFULLY WITH ALL 3 TIERS         ")
        print("============================================================")

    except HttpError as error:
        print(f"\n[ERROR] Deployment failed: {error}")

if __name__ == '__main__':
    deploy_3tier_enterprise_classroom()
