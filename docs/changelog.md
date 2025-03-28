# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2025-03-26

### Added
- New UDM ingestion functionality with `ingest_udm` method for sending structured events directly to Chronicle
- Support for ingesting both single UDM events and multiple events in batch
- Automatic generation of event IDs and timestamps for UDM events when missing
- Input validation to ensure correct UDM event structure and required fields
- Deep-copying of events to prevent modification of original objects
- Comprehensive unit tests and integration tests for UDM ingestion
- Detailed examples in README.md showing UDM event creation and ingestion
- New example in `example.py` demonstrating the creation and ingestion of various UDM event types

- New log ingestion functionality with `ingest_log` method for sending raw logs to Chronicle
- Support for multiple log formats including JSON, XML, and other string raw log types
- Forwarder management with `get_or_create_forwarder`, `create_forwarder`, and `list_forwarders` methods
- Log type utilities for discovering and validating available Chronicle log types
- Custom timestamp support for log entry time and collection time
- Comprehensive examples in README.md showing various log ingestion scenarios
- Example usage in `example.py` demonstrating log ingestion for OKTA and Windows Event logs

## [0.1.3] - 2024-03-25

### Added
- New natural language search functionality with `translate_nl_to_udm` and `nl_search` methods
- Ability to translate natural language queries to UDM search syntax
- Integration with existing search capabilities for seamless NL-powered searches
- Comprehensive documentation in README.md with examples and query patterns
- Example usage in `example.py` demonstrating both translation and search capabilities
- Improved command-line parameters in examples for easier customization

## [0.1.2] - 2024-03-17

### Added
- New `validate_rule` method in Chronicle client for validating YARA-L2 rules before creation or update
- Support for detailed validation feedback including error positions and messages
- Example usage in `example_rule.py` demonstrating rule validation
- Comprehensive documentation for rule validation in README.md

### Changed
- Enhanced rule management functionality with validation capabilities
- Improved error handling for rule-related operations
