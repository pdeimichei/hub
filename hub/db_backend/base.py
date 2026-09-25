"""PostgreSQL backend that uses an Azure managed-identity access token."""

from azure.identity import DefaultAzureCredential
from django.db.backends.postgresql.base import DatabaseWrapper as PostgreSQLDatabaseWrapper

POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"
_credential = DefaultAzureCredential()


class DatabaseWrapper(PostgreSQLDatabaseWrapper):
    """
    Fetch a fresh Entra token whenever Django opens a PostgreSQL connection.

    PostgreSQL Flexible Server accepts the token in the password field.
    """

    def get_connection_params(self):
        params = super().get_connection_params()
        params["password"] = _credential.get_token(POSTGRES_SCOPE).token
        return params
