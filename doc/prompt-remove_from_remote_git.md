how can I remove latest commit from my repo on Github?
I don't want to revert a commit.
I want to remove it from local and remote repo entirely.
In the last commit I've pushed multiple large files to Github.
I want to remove those files entirely together with the whole commit.
So if I clone the repo .git doesn't contain any refernces to this commit and its files.
I'm the only developer using this repo so I can safely rewrite git history
Provide links that confirm your solution will work.

C:
git reset --hard HEAD~1
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch <file-path>' --prune-empty --tag-name-filter cat -- --all
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --prune=now
git gc --aggressive --prune=now
git push origin --force --all

Q:
your solution requires to specify all the files I want to remove explicitly. Beside the large files there were many small files which I want also to remove. I need a commands that will remove all changes included in the commit

C:
git reset --hard HEAD~1
git push origin --force

Q:
actually I've added subtree as follows
git subtree add --prefix .github/actions/docker-login https://github.com/docker/login-action.git v3 --squash
Now I want to remove it entirely including any reference to files from this subtree in .git.
Also I want to remove it from remote repo

C:
Find the commit hash of the commit just before the subtree addition. Let's assume the hash is abc123.
git reset --hard abc123
rm -rf .github/actions/docker-login
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .github/actions/docker-login' --prune-empty --tag-name-filter cat -- --all
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --prune=now
git gc --aggressive --prune=now
git push origin --force --all

Q:
analyse following alternative solution and tell if it will also work or it will fail to comply with my requirements of removing all the files from git subtree locally and remotely
<DS solution>
C:
Recommends DS solution

Q:
I want to run following git command
git filter-repo --path .github/actions/docker-login/ --invert-paths
Do I have to install first:
pip install git-filter-repo
I assume git-filter-repo is a Python program
How git will access this program?
Will pip install it to global Windows PATH?
If I don't want use it in globally how can install it to make available only locally?

___

DS:
git reset --hard HEAD~1
git push --force origin <branch-name>  # Replace <branch-name> with your branch (e.g., main, master)
git gc --prune=now

pip install git-filter-repo
git filter-repo --path-glob '*.large' --invert-paths  # Replace `*.large` with your file patterns
git push --force --all origin  # Force-push all branches
git push --force --tags origin # Force-push tags (if any)

Verification
git clone <your-repo-url>
git log --stat  # No trace of the files should appear
find . -name "*.large"  # Replace with your file pattern

Q:
actually I've added subtree as follows
git subtree add --prefix .github/actions/docker-login https://github.com/docker/login-action.git v3 --squash
Now I want to remove it entirely including any reference to files from this subtree in .git.
Also I want to remove it from remote repo

DS:

* Install git-filter-repo if not already installed

pip install git-filter-repo

* Run filter-repo to remove the subtree directory and its history

git filter-repo --path .github/actions/docker-login/ --invert-paths

git push --force --all origin       # Force-push all branches
git push --force --tags origin      # Force-push tags (if any)

git reflog expire --expire=now --all
git gc --prune=now

Q:
analyse following alternative solution and tell if it will also work or it will fail to comply with my requirements of removing all the files from git subtree locally and remotely
<C solution>

DS:
> After resetting to abc123 and deleting the subtree directory:

git filter-repo --path .github/actions/docker-login --invert-paths
git push --force --all origin

Recommends DS solution

Q:
I want to run following git command
git filter-repo --path .github/actions/docker-login/ --invert-paths
Do I have to install first:
pip install git-filter-repo
I assume git-filter-repo is a Python program
How git will access this program?
Will pip install it to global Windows PATH?
If I don't want use it in globally how can install it to make available only locally?

DS:
python -m venv myenv
myenv\Scripts\activate
pip install git-filter-repo
git filter-repo --version

Q:
ok, so I want to use git filter-repo solution.
Below provide all steps required to undo all changes introduced by:
git subtree add --prefix .github/actions/docker-login https://github.com/docker/login-action.git v3 --squash
Also I want to install git-filter-repo only within Python VirtualEnv.
But I want it to work with git

DS:
python -m venv myenv
myenv\Scripts\activate
pip install git-filter-repo
git filter-repo --version

* Remove the subtree directory and rewrite all commits

git filter-repo --path .github/actions/docker-login --invert-paths

* Force-push the rewritten history to GitHub (replace "main" with your branch)

git push origin --force --all
git push origin --force --tags  # If you have tags

* Prune orphaned objects and optimize the repository

git reflog expire --expire=now --all
git gc --prune=now
git gc --aggressive --prune=now
deactivate  # Exit the virtual environment
rm -rf ~/git-filter-env  # Delete the environment

* Fresh clone to confirm files are gone

cd ..
git clone <your-repo-url> test-clone
cd test-clone
ls -la .github/actions/docker-login  # Should show "No such file or directory"

