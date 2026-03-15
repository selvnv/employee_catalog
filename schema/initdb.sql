CREATE USER catalog_app WITH PASSWORD 'catalog_app';
CREATE DATABASE employees OWNER catalog_app;
GRANT ALL PRIVILEGES ON DATABASE employees TO catalog_app;