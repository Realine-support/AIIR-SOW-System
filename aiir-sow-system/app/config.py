"""
Configuration module for AIIR SOW System
Loads environment variables and provides typed configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Config(BaseSettings):
    """
    Application configuration loaded from environment variables
    """

    # === OpenAI Configuration ===
    openai_api_key: str

    # === Google Cloud Configuration ===
    google_credentials_path: str
    google_service_account_email: str

    # === Google Drive/Sheets IDs ===
    tracker_sheet_id: str
    tracker_tab_name: str = "Tracker"
    calculator_sheet_id: str
    calculator_tab_name: str = "Calculator"

    # === Shared Drive ===
    shared_drive_id: str

    # === Template IDs ===
    calculator_template_id: str
    sow_template_doc_id: str

    # === Folder IDs (All in Shared Drive) ===
    transcripts_folder_id: str
    rationales_folder_id: str
    sow_templates_folder_id: str
    client_documents_folder_id: str
    client_master_folder_id: str
    archive_folder_id: str

    # === Email Configuration ===
    gmail_send_as: str
    review_email_to: str
    client_email_from: str

    # === Gmail OAuth2 Configuration (Optional) ===
    gmail_use_oauth2: bool = False
    gmail_refresh_token: Optional[str] = None
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None

    # === Upstash Redis Configuration ===
    upstash_redis_rest_url: str
    upstash_redis_rest_token: str

    # === Webhook URLs ===
    base_url: str = "http://localhost:8000"
    approve_pricing_webhook_url: Optional[str] = None
    approve_sow_webhook_url: Optional[str] = None

    # === Application Configuration ===
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Auto-generate webhook URLs if not provided
        if not self.approve_pricing_webhook_url:
            self.approve_pricing_webhook_url = f"{self.base_url}/webhooks/approve-pricing"
        if not self.approve_sow_webhook_url:
            self.approve_sow_webhook_url = f"{self.base_url}/webhooks/approve-sow"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"


# Global configuration instance
# This will be initialized when the module is imported
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance
    Creates it if it doesn't exist
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """
    Force reload configuration from environment
    Useful for testing
    """
    global _config
    _config = Config()
    return _config
