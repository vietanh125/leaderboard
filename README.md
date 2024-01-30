# Chai Competition Leaderboard Webapp

Host a web-based leaderboard for Chai competition using Gradio. The structure is simple, `fetch_data.py` loops infinitely to fetch the latest results and save it to `db.csv`. This script is basically a copy-paste of [chai-guanaco](https://github.com/chai-research/chai-guanaco/) package with all the caching removed. `app.py` loads the csv file and hosts a webapp using Gradio.

### Run the project
```commandline
pip install -r requirements.txt
```
In one terminal, execute this command to fetch and save leaderboard data:
```commandline
python fetch_data.py
```
In another terminal, execute this bash file to tunnel the app:
```
./auto_ssh.sh
```