import subprocess

def terminal_cmd(command, timeout_s: int|float|None = None):
    try:
        if timeout_s is not None:
            result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True, timeout=timeout_s)
        else:
            result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        # print("Standard Output:")
        return result.stdout
        # print("Standard Error:")
        # print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        print(f"Error output: {e.stderr}")

recieved_topics = terminal_cmd("ros2 topic list").split("\n")
for topic in recieved_topics:
    if topic != '':
        topic_type = terminal_cmd(f"ros2 topic type {topic}")
        topic_params = terminal_cmd(f"ros2 interface show {topic_type}")
        print(f"{topic}") 
        print(f"{topic_type}")
        print(f"{topic_params}")
        print("-"*30)