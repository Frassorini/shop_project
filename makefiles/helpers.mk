ifndef _HELPERS_MK_INCLUDED
_HELPERS_MK_INCLUDED := 1

include makefiles/config.mk

define ask_confirmation_if_prod
@if [ "$(call get_mode)" = "PROD" ]; then \
    read -p "You are in PROD mode! Are you sure? [y/N] " ans; \
    if [ "$$ans" != "y" ]; then echo "Aborted"; exit 1; fi; \
fi
endef

define ask_confirmation
	@echo -n "$(1) [y/N]: "; \
	read ans; \
	case "$$ans" in \
		[yY]) ;; \
		*) echo "Aborted"; exit 1 ;; \
	esac
endef


define newline


endef

endif