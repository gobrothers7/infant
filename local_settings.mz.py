DEBUG = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "e788d084-aba4-4bc4-bb97-7dfbc27a1dea9070e0f8-0a35-4837-820f-28398764275790dcfb0b-f8fc-47b4-b9c7-7af306b061d5"
NEVERCACHE_KEY = "2ab57d6d-b4fd-417f-8c9f-7a51722ede7c59627035-f3d5-4614-9024-acac09f977c299feeff8-95e0-4cce-b0f8-014680b219df"

DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": "dev.db",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}
