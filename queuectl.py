import sys
import subprocess
import time
import signal
from db import (
    init_db,
    add_job,
    get_next_job,
    update_job_state,
    list_jobs
)


init_db()


stop_worker = False



def enqueue_job(cmd):
    job_id = add_job(cmd)
    print(f"Job added successfully (ID: {job_id})")


#LIST JOBS---------------------------------------------------------------------------------------
def show_jobs(state=None):
    jobs = list_jobs(state)
    if not jobs:
        print("No jobs found.")
        return

    print(f"{'ID':36} {'STATE':10} {'ATTEMPTS':8} COMMAND")
    print("-" * 80)
    for job in jobs:
        print(f"{job['id']:36} {job['state']:10} {job['attempts']:<8} {job['command']}")


# WORKER----------------------------------------------------------------------------------------
def start_worker():
    global stop_worker

    def handle_signal(sig, frame):
        global stop_worker
        stop_worker = True
        print("\n Worker shutting down gracefully...")

    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, handle_signal)

    print("Worker started. Waiting for jobs... (Press Ctrl+C to stop)")

    while not stop_worker:
        job = get_next_job()
        if not job:
            time.sleep(2)
            continue

        job_id = job["id"]
        cmd = job["command"]
        attempts = job["attempts"]
        max_retries = job["max_retries"]

        print(f"\n Running job {job_id}: {cmd}")
        update_job_state(job_id, "processing")

        try:
            result = subprocess.run(cmd, shell=True)
            if result.returncode == 0:
                print(f"Job {job_id} completed successfully.")
                update_job_state(job_id, "completed")
            else:
                attempts += 1
                print(f"Job {job_id} failed (Attempt {attempts}/{max_retries}).")

                if attempts < max_retries:
                    delay = 2 ** attempts 
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    update_job_state(job_id, "pending", attempts)
                else:
                    print(f"Job {job_id} moved to DLQ (Dead Letter Queue).")
                    update_job_state(job_id, "dead", attempts)

        except Exception as e:
            print(f"Error executing job {job_id}: {e}")
            update_job_state(job_id, "dead", attempts + 1)

    print("Worker stopped.")


#DLQ---------------------------------------------------------------------------------------------
def list_dlq():
    jobs = list_jobs("dead")
    if not jobs:
        print("No jobs in Dead Letter Queue.")
        return

    print(f"{'ID':36} {'STATE':10} {'ATTEMPTS':8} COMMAND")
    print("-" * 80)
    for job in jobs:
        print(f"{job['id']:36} {job['state']:10} {job['attempts']:<8} {job['command']}")


#CLI HANDLER----------------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("""
Usage:
  python queuectl.py enqueue "<command>"   → Add a new job
  python queuectl.py list [state]          → List all jobs (or by state)
  python queuectl.py worker                → Start worker to process jobs
  python queuectl.py dlq                   → Show Dead Letter Queue
        """)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "enqueue":
        if len(sys.argv) < 3:
            print("Please provide a command to enqueue.")
        else:
            enqueue_job(sys.argv[2])

    elif command == "list":
        state = sys.argv[2] if len(sys.argv) > 2 else None
        show_jobs(state)

    elif command == "worker":
        start_worker()

    elif command == "dlq":
        list_dlq()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
