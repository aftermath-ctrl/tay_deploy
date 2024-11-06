# fin_agent/management/commands/setup_templates.py

from django.core.management.base import BaseCommand
from accounts.models import PromptTemplate

class Command(BaseCommand):
    help = 'Creates default prompt templates'

    def handle(self, *args, **kwargs):
        PromptTemplate.create_default_templates()
        self.stdout.write(self.style.SUCCESS('Successfully created default templates'))