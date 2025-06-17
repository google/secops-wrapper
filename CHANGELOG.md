# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-06-16
### Added
- New Data Table functionality for managing structured data in Secops
  - Support for creating, retrieving, listing, and deleting data tables
  - Multiple column types (STRING, REGEX, CIDR) with proper validation
  - Efficient batch processing for row operations with automatic chunking
  - Data scope management for access control
- Enhanced Reference List capabilities for simple value lookups in Secops
  - Create, update, list, and delete reference lists with proper validation
  - Support for three syntax types: STRING, REGEX, and CIDR patterns
  - View control options (BASIC/FULL) for efficient list management
  - Proper validation of CIDR entries to prevent invalid data
- Comprehensive integration with SecOps's detection rule system
- Example script `data_tables_and_reference_lists.py` demonstrating all functionality
- Extensive documentation in README.md with usage examples and best practices

## [0.2.0] - 2025-05-31
### Added
- Support for "dev" and "staging" regions with special URL formats
- Updated documentation with new region options and usage examples

## [0.1.16-17] - 2025-05-24
### Fixed
- Fixed timestamp format in `get_alerts` to handle timezone conversion, include 'Z' suffix, and remove microseconds, resolving API compatibility issues

## [0.1.15] - 2025-05-04
### Added
- CLI support for log labels with `--labels` flag in the `log ingest` command
- Support for both JSON format and key=value pair format for labels
- Updated documentation in CLI.md for label usage
- Integration tests for verifying CLI label functionality

## [0.1.14] - 2025-05-04
### Added
- New `search_rules` functionality to find rules using regex patterns
- Enhanced rule management with ability to search rule content
- CLI command for rule searching with regex pattern matching

## [0.1.13] - 2025-04-22
### Fixed
- Added retry mechanism for 429 (rate limit) errors in natural language search
- Implemented 5-second backoff with up to 5 retry attempts for both translation and search
- Enhanced error detection to handle both HTTP 429 codes and "RESOURCE_EXHAUSTED" error messages
- Improved resilience against intermittent rate limiting in Chronicle API calls

## [0.1.12] - 2025-04-18
### Added
- Support for ingest labels

## [0.1.11] - 2025-04-17
### Fixed
- Bugs in type handling for strict builder

## [0.1.9] - 2025-04-15

### Added
- Enhanced CLI configuration functionality with support for time-related parameters
- Added ability to store default `--start-time`, `--end-time`, and `--time-window` in CLI configuration
- Improved CLI flag flexibility with support for both kebab-case and snake_case formats
- CLI now accepts both `--flag-name` and `--flag_name` formats for all command line arguments
- Support for both space-separated (`--flag value`) and equals syntax (`--flag=value`) for all CLI arguments
- Comprehensive CLI documentation covering all available commands and options
- Added examples for all CLI commands in documentation

### Fixed
- Resolved error in entity command when handling AlertCount objects
- Improved error handling for unsupported entity types
- Enhanced handling of prevalence data in entity summaries
- Fixed serialization issues in CLI output formatting
- Improved data export log type handling with better validation
- Enhanced error messages for data export commands with troubleshooting guidance
- Added more robust log type formatting in Chronicle API client
- Updated CSV export examples to use correct snake_case UDM field names

## [0.1.8] - 2025-04-15

### Added
- New Gemini AI integration providing access to Chronicle's conversational AI interface
- `gemini()` method for querying the Gemini API with natural language questions
- Automatic user opt-in to Gemini functionality when first used
- Manual opt-in method `opt_in_to_gemini()` for explicit user control
- Structured response parsing with TEXT, CODE, and HTML block handling
- Smart extraction of text content from both TEXT and HTML blocks with HTML tag stripping
- Helper methods for accessing specific content types: `get_text_content()`, `get_code_blocks()`, `get_html_blocks()`
- Access to raw API responses via `get_raw_response()` for advanced use cases
- Comprehensive documentation and examples for Gemini functionality


## [0.1.6] - 2025-04-10

### Added
- Enhanced log ingestion with batch processing capability for improved performance
- Support for ingesting multiple logs in a single API call through the existing `ingest_log` method
- Backward compatibility maintained for single log ingestion
- New Data Export API integration for exporting Chronicle logs to Google Cloud Storage
- Methods for creating, monitoring, and canceling data exports
- Support for exporting specific log types or all logs within a time range
- Comprehensive documentation and examples for Data Export functionality

### Fixed
- Resolved issues with entity summary functionality for improved entity lookups and correlation
- Fixed incorrect handling of entity relationships in entity summaries
- Corrected statistics query processing bug that affected aggregation results
- Improved error handling for statistics queries with complex aggregations

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
