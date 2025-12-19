ifndef _UTILS_MK_INCLUDED
_UTILS_MK_INCLUDED := 1

format: ## Run pre-commit
	poetry run pre-commit run --all-files

endif