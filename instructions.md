# Database Schema Instructions

## Table: owners_draw_allocations

* id: INTEGER PRIMARY KEY
* timestamp: TEXT
* client_name: TEXT
* form_name: TEXT
* transaction_id: TEXT UNIQUE
* allocated_amount: REAL
* allocation_description: TEXT

## Table: classroom_student_telemetry

* id: INTEGER PRIMARY KEY
* timestamp: TEXT
* student_id: TEXT UNIQUE
* student_name: TEXT
* course_name: TEXT
* attendance_score: REAL
* grade_score: REAL

## Table: swarm_task_logs

* id: INTEGER PRIMARY KEY
* timestamp: TEXT
* task_id: TEXT UNIQUE
* intent: TEXT
* agent_gem: TEXT
* status: TEXT
* output: TEXT
* refinements: INTEGER
