import os
from website import create_app
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("/home/ec2-user/junseo-yang-portfolio/.env") 
load_dotenv(dotenv_path=env_path)

app = create_app('production')

if __name__ == "__main__":
    app.run()
