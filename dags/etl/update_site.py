import datetime
from git import Repo

def push_to_git():
    try:
        repo = Repo(os.environ.get("GIT_REPO_PATH"))
        repo.git.add("docs/today.json")
        repo.index.commit("New data")
        origin = repo.remote(name="origin")
        origin.push()
    except Exception as e:
        now = datetime.datetime.now()
        nowstr = now.strftime("%Y_%m_%d_%H_%M")
        with open(f"error_{nowstr}.txt", "a") as f:
            f.write(f"{nowstr}: {e}\n")