# Azure beta deployment

The `azure-beta` branch is the Azure-native version of Hub.

## Identity model

- End users authenticate with Microsoft Entra ID through Azure App Service Authentication (Easy Auth).
- Access is controlled by assignment to the Entra enterprise application/group.
- Django does not own end-user passwords in Azure.
- The App Service uses its system-assigned managed identity to authenticate to Azure Database for PostgreSQL.
- PostgreSQL can therefore run in Microsoft-Entra-only mode without storing a database password in App Service.

## Required App Service settings

```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<random secret>
AZURE_ENTRA_AUTH=True
AZURE_POSTGRES_ENTRA=True

DB_NAME=hub
DB_USER=<PostgreSQL role mapped to the App Service managed identity>
DB_HOST=<server>.postgres.database.azure.com
DB_PORT=5432
DB_SSLMODE=require
DB_CONN_MAX_AGE=300
```

Do not set `DB_PASSWORD` in Azure when Entra-only PostgreSQL authentication is enabled.

App Service automatically supplies `WEBSITE_HOSTNAME`; Django adds it to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.

## Startup command

Configure App Service startup command as:

```
bash startup.sh
```

The startup script collects static files, applies Django migrations, creates/updates the `giacenza` schema, and starts Gunicorn.

## PostgreSQL managed identity

Before the app can connect, the App Service system-assigned identity must be created as a Microsoft Entra principal inside PostgreSQL. The PostgreSQL role name used there must match `DB_USER`.

## Local development

Local development keeps the original password-based setup:

```
AZURE_ENTRA_AUTH=False
AZURE_POSTGRES_ENTRA=False
DB_USER=postgres
DB_PASSWORD=...
```

Django local login/admin remains available only when `AZURE_ENTRA_AUTH=False`.
