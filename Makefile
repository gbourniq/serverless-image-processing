# Set shell
SHELL=/bin/bash -e -o pipefail

include utils/helpers.mk

# Conda environment
CONDA_ENV_NAME=image-processing
CONDA_CREATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda env create
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate

### Environment, githooks, and dependencies ###
.PHONY: env pre-commit sls-plugins
env:
	@ ${INFO} "Creating ${CONDA_ENV_NAME} conda environment and installing poetry dependencies"
	@ conda env create -f environment.yml -n $(CONDA_ENV_NAME)
	@ ($(CONDA_ACTIVATE) $(CONDA_ENV_NAME); poetry install)
	@ ${SUCCESS} "Please activate the environment with: conda activate ${CONDA_ENV_NAME}"
 
pre-commit:
	pre-commit install -t pre-commit -t commit-msg

# sls plugin install -n serverless-python-requirements
sls-plugins:
	npm install serverless-s3-remover

### Development ###
.PHONY: lint test cov

lint:
	pre-commit run --all-files

test:
	pytest .

cov:
	open htmlcov/index.html


### Deployment ###

build:
	@ rm -rf bin && mkdir -p bin/lambda-layer/python
	@ poetry export -f requirements.txt --output bin/lambda-layer/requirements.txt
	@ docker run --rm \
		-v $$(pwd):/foo \
		-w /foo \
		lambci/lambda:build-python3.8 \
		pip install -r bin/lambda-layer/requirements.txt --target bin/lambda-layer/python
	@ echo "Built dependencies into bin/lambda-layer/python"

deploy:
	sls deploy -v

deploy-hello-function:
	sls deploy function -f hello-world -v

invoke-hello-function:
	sls invoke local -f hello-word -l
	sls invoke -f hello-word -l

logs:
	serverless logs -f hello-world -t

remove-service:
	sls remove -v
