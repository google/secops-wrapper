# Google SecOps SDK for Python

Welcome to the documentation for the Google SecOps SDK for Python. This SDK provides a comprehensive interface for interacting with Google Security Operations products, currently supporting Chronicle/SecOps SIEM.

## Overview

The Google SecOps SDK for Python wraps the API for common use cases, including:

- UDM searches
- Entity lookups
- IoCs management
- Alert management
- Case management
- Detection rule management

## Getting Started

- [Installation](installation.md)
- [Authentication](authentication.md)
- [Quick Start](quickstart.md)

## Core Features

- [Chronicle Client](chronicle/index.md)
- [Log Ingestion](chronicle/ingestion.md)
- [UDM Search](chronicle/search.md)
- [IoCs Management](chronicle/iocs.md)
- [Alert Management](chronicle/alerts.md)
- [Case Management](chronicle/cases.md)
- [Detection Rules](chronicle/rules.md)
- [Entity Graph](chronicle/entity.md)
- [Retrohunts](chronicle/retrohunts.md)

## CLI Reference

- [Command Line Interface](cli/index.md)
- [CLI Commands](cli/commands.md)

## Advanced Topics

- [Proxy Configuration](advanced/proxies.md)
- [Regional Endpoints](advanced/regions.md)
- [Error Handling](advanced/errors.md)
- [Pagination](advanced/pagination.md)

## API Reference

- [API Documentation](api/index.md)

## Contributing

- [Contributing Guide](contributing.md)
- [Development Setup](development.md)
- [Changelog](changelog.md)

```{toctree}
:maxdepth: 2
:hidden:

installation
authentication
quickstart
chronicle/index
cli/index
advanced/index
api/index
contributing
development
changelog
```
