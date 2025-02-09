# homer.py
import time
import random

def home_task2(update_progress):
    total_steps = random.randint(10,50)  # Example total steps
    for step in range(total_steps):
        fuctionC()  # Simulate work
        # Report progress: current step (1-based), total steps
        update_progress(current=step + 1, total=total_steps)


def collect1():
    time.sleep(5)

def home_task(update_progress):
    total_steps = 100  # Estimated number of steps, you can adjust based on how frequently you want updates
    step = 50
    update_progress(current=step, total=total_steps, result= 'Fetching metadata')
    collect1()
    update_progress(current=step, total=total_steps, result= 'Download started')
    
    while step < total_steps:
        # Simulate part of functionC working (replace with actual function logic)
        time.sleep(random.randint(1,2))  # Simulate time taken for each step
        
        step += 1
        update_progress(current=step, total=total_steps, result= 'Download is in progress')
        
    update_progress(current=total_steps, total=total_steps, result= 'Download completed')
