from website import create_app
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("/home/junseoyang/Documents/junseo-yang-portfolio/junseo-yang-portfolio/.env") 
load_dotenv(dotenv_path=env_path)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
