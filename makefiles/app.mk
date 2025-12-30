ifndef _APP_MK_INCLUDED
_APP_MK_INCLUDED := 1

asgi-dev-manager: ## Run development ASGI server for manager subject
	SUBJECT_MODE=MANAGER ENV_FILE=environment/.env.dev poetry run uvicorn shop_project.main:create_app --reload --port 8001

asgi-dev-employee: ## Run development ASGI server for employee subject
	SUBJECT_MODE=EMPLOYEE ENV_FILE=environment/.env.dev poetry run uvicorn shop_project.main:create_app --reload --port 8002

asgi-dev-customer: ## Run development ASGI server for customer subject
	SUBJECT_MODE=CUSTOMER ENV_FILE=environment/.env.dev poetry run uvicorn shop_project.main:create_app --reload --port 8003

endif