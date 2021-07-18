# SDA coding challenge

Install virtual environment and requirements like this: 

```bash
pyenv local 3.8.5
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

or via Makefile:

```bash
make setup
```

Activate the environment
```bash
source .venv/bin/activate
```
  and open yolo_case.ipynb in jupyter(lab) to see the results and explanation.

On windows use
```bash
jupyter-lab --no broswer
```
and copy the http line into browser.

On linux and apple use
```bash
jupyter-lab 
```