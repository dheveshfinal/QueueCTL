# QueueCTL — Lightweight Background Job Queue (SQLite Based)

QueueCTL is a simple background job queue built with Python and SQLite.  
It supports job enqueueing, retry with exponential backoff, dead letter queues (DLQ), persistent storage, configuration, metrics, and graceful worker shutdown.  

## 1. Setup Instructions

### Requirements
- Python 3.10 or higher
- No external dependencies (only standard library)

### Installation
Clone or copy the project folder:
```bash
git clone <repo-url>
cd assignment

python queuectl.py enqueue "invalidcommand arg1"
Job added successfully (ID: 80e02acd-8be6-4737-b94e-4753ad852d5c)

### output
python queuectl.py worker
Worker started. Waiting for jobs... (Press Ctrl+C to stop)
 Running job 80e02acd-8be6-4737-b94e-4753ad852d5c: invalidcommand arg1
'invalidcommand' is not recognized as an internal or external command,
operable program or batch file.
Job 80e02acd-8be6-4737-b94e-4753ad852d5c failed (Attempt 1/3).
Retrying in 2 seconds...

 Running job 80e02acd-8be6-4737-b94e-4753ad852d5c: invalidcommand arg1
'invalidcommand' is not recognized as an internal or external command,
operable program or batch file.
Job 80e02acd-8be6-4737-b94e-4753ad852d5c failed (Attempt 2/3).
Retrying in 4 seconds...

 Running job 80e02acd-8be6-4737-b94e-4753ad852d5c: invalidcommand arg1
'invalidcommand' is not recognized as an internal or external command,
operable program or batch file.
Job 80e02acd-8be6-4737-b94e-4753ad852d5c failed (Attempt 3/3).
Job 80e02acd-8be6-4737-b94e-4753ad852d5c moved to DLQ (Dead Letter Queue).


python queuectl.py dlq
ID                                   STATE      ATTEMPTS COMMAND
--------------------------------------------------------------------------------
80e02acd-8be6-4737-b94e-4753ad852d5c dead       3        invalidcommand arg1




