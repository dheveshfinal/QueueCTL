# QueueCTL (SQLite Based)

QueueCTL is a simple background job queue built with Python and SQLite.  
It supports job enqueueing, retry with exponential backoff, dead letter queues (DLQ), persistent storage, configuration, metrics, and graceful worker shutdown.  

## 1. Setup Instructions

### Requirements
- Python 3.10 or higher
- No external dependencies (only standard library)

### Installation
Clone or copy the project folder:
```bash
git clone https://github.com/dheveshfinal/QueueCTL.git
cd assignment


1. Enqueue a Job

Add a command to the queue for processing:

python queuectl.py enqueue "echo Hello Queue"

Output:

Job added successfully (ID: 7eaf62c3-5a92-4a5d-9f84-13c1c26f8b2f)


2. Start the Worker

Run the worker to process queued jobs:

python queuectl.py worker

Output:
Worker started. Waiting for jobs... (Press Ctrl+C to stop)
Running job 7eaf62c3-5a92-4a5d-9f84-13c1c26f8b2f: echo Hello Queue
Hello Queue
Job 7eaf62c3-5a92-4a5d-9f84-13c1c26f8b2f completed successfully.


3. Handling Invalid Commands

If an invalid command is enqueued, QueueCTL will automatically retry it before moving it to the Dead Letter Queue (DLQ).

python queuectl.py enqueue "invalidcommand arg1"

Output:
Job added successfully (ID: 80e02acd-8be6-4737-b94e-4753ad852d5c)


Then, when the worker runs:

python queuectl.py worker

Output:
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

4. Viewing the Dead Letter Queue

List all failed jobs that reached the DLQ:

python queuectl.py dlq

Output:
ID                                   STATE      ATTEMPTS COMMAND
--------------------------------------------------------------------------------
80e02acd-8be6-4737-b94e-4753ad852d5c dead       3        invalidcommand arg1



 Architecture Overview

+-------------+       +-------------+       +-------------+
|  Enqueue    | --->  |   Queue DB  | --->  |   Worker    |
+-------------+       +-------------+       +-------------+
                                             |
                                             v
                                        +----------+
                                        |   DLQ    |
                                        +----------+


Enqueue: Adds jobs to the queue.

Queue DB: Stores pending, active, and completed job states.

Worker: Executes jobs and retries failures.

DLQ: Collects jobs that permanently fail after all retries.

 Assumptions & Trade-offs
Area	Choice	Reason
Storage	SQLite / JSON file	Lightweight and easy to manage locally
Retries	3 attempts with exponential backoff	Prevents infinite loops and server overload
Execution	Subprocess execution of commands	Flexible for various system commands
DLQ	Manual inspection and replay	Keeps control in user’s hands
 Testing Instructions




Run Unit Tests

pytest

Manual Verification

Enqueue valid and invalid commands.

Observe worker behavior and retry logic.

Check DLQ for failed jobs.
