"""Service for handling terms & conditions business logic."""

# pylint:disable=import-error,protected-access

from .base_service import BaseService


class TermConditionService(BaseService):
    """Service for term & conditions operations."""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "website"
        self.fields = ["id", "term_and_condition"]
        self.website = self._get_current_website()

    def get_term_string(self):
        """Retrieve relative domain of current website's term and conditions"""
        self.default_domain = [("id", "=", self.website.id)]
        result = self.search()
        return result.term_and_condition if result else None
