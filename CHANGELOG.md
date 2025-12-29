# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.31.0] - 2025-12-29
### Added
- Support for list featured content rules method

## [0.30.0] - 2025-12-22
### Added
- Support for following watchlist management methods:
  - List watchlists
  - Create watchlist
  - Get watchlist details
  - Update watchlist
  - Delete watchlist

## [0.29.0] - 2025-12-17
### Added
- Support for following log/data processing pipeline methods:
  - List pipelines
  - Create pipeline
  - Get pipeline details
  - Update pipeline
  - Delete pipeline
  - Associate stream to pipeline
  - Dissociate stream from pipeline
  - Fetch associated pipeline using stream
  - Fetch sample logs by stream
  - Test pipeline

## [0.28.1] - 2025-12-11
### Updated
- CLI to show help when required sub-command/argument not provided.

## [0.28.0] - 2025-12-10
### Updated
- Minimum python version support to 3.10 from 3.9 as python 3.9 has reached its end of life.

## [0.27.2] - 2025-12-08
### Updated
- Parser list method to handle pagination properly
  - Method auto paginates and returns all when no page size is provided.
  - When page size is provided, method returns response with next page token.

## [0.27.1] - 2025-12-05
### Updated
- Updated Chronicle client to expose API version param for following:
  - Feed management (list, get, create, delete, disable, enable, generate secret)
  - Reference list management(create, get, list, update)
  - Rule management (create, get, list, update, delete, search)
  - Rule deployment (get, update)
  - Rule retrohunt (create, get)

## [0.27.0] - 2025-12-05
### Added
- Chronicle configuration for default API endpoint version to use for all methods
### Updated
- Following module's methods to add support for configuring API endpoint version:
  - Feed management (list, get, create, delete, disable, enable, generate secret)
  - Reference list management(create, get, list, update)
  - Rule management (create, get, list, update, delete, search)
  - Rule deployment (get, update)
  - Rule retrohunt (create, get)

## [0.26.0] - 2025-11-26
### Added
- Search curated rule detection method support
### Updated
- Curated rules/rule category/rule deployment related list methods to return page token for paginated requests.

## [0.25.2] - 2025-11-20
### Updated
- CLI with better modularity for improved development and maintenance support.

## [0.25.1] - 2025-11-17
### Fixed
- Request retry logging for no response

## [0.25.0] - 2025-11-14
### Updated
- Log type methods to use API instead of static list

## [0.24.0] - 2025-11-07
### Added
- Support for bulk update data table rows

## [0.23.0] - 2025-11-04
### Added
- Support for following methods:
  - List Curated Rules
  - Get Curated Rule
  - Get Curated Rule By Name
  - List Curated Rule Sets
  - Get Curated Rule Set
  - List Curated Rule Set Categories
  - Get Curated Rule Set Category
  - List Curated Rule Set Deployments
  - Get Curated Rule Set Deployment
  - Get Curated Rule Set Deployment By Name
  - Updated Curated Rule Set Deployment

## [0.22.0] - 2025-10-30
### Added
- Support for entity import method

## [0.21.2] - 2025-10-15
### Added
- Support for filter in list rule deployments method

## [0.21.1] - 2025-10-13
### Fixed
- List rules and rule deployments for empty response

## [0.21.0] - 2025-10-10
### Added
- Support for list and update method in data export
### Updated
- Data export methods to utilize enhanced endpoint and parameters

## [0.20.2] - 2025-10-06
### Updated
- Data table rows bulk replace larger rows handling.

## [0.20.1] - 2025-09-26
### Fixed
- Data table rows bulk replace for larger row count.

## [0.20.0] - 2025-09-25
### Added
- Support for fetch UDM search view method

## [0.19.1] - 2025-09-19
### Fixed
- Create data export for all log types flag

## [0.19.0] - 2025-09-18
### Added
- Support for export native dashboard method

## [0.18.2] - 2025-09-16
### Updated
- CLI for better help message on unauthenticated commands
- CLI to show help for `secops log` command without sub-command

## [0.18.1] - 2025-09-15
### Added
- Support for entity mapping and column options in Data table creation

## [0.18.0] - 2025-09-12
### Added
- Added support for following Rule Deployment methods
  - Get rule deployment details
  - List rule deployments
  - Update rule deployment
  - Set rule alerting

## [0.17.0] - 2025-09-11
### Added
- Default retry mechanism for all SecOps requests
## Updated
- Clients (SecOpsClient, ChronicleClient) to accept user define retry configuration

## [0.16.0] - 2025-09-10
### Added
- Support for import native dashboard method
### Fixed
- Data Table create method scopes parameter

## [0.15.0] - 2025-09-04
### Added
- Support for following forwarder methods:
  - Patch forwarder
  - Delete forwarder
- CLI command for following forwarder:
  - Create forwarder
  - Get forwarder
  - List Forwarder
  - Get Or Create forwarder
- Chronicle client methods for forwarder:
  - Create forwarder
  - Get forwarder
  - List forwarder

## [0.14.2] - 2025-09-03
### Added
- Support for list basis and time window params in list detections method.

## [0.14.1] - 2025-09-01
### Updated
- Log ingestion to support multi logs string.

## [0.14.0] - 2025-08-26
### Added
- Update Data table properties method
- Data table rows bulk replace method

## [0.13.0] - 2025-08-18
### Added
- Find UDM Field Values functionality

## [0.12.3] - 2025-08-13
### Updated
- Dev Base URL with HTTPS

## [0.12.2] - 2025-08-13
### Updated
- Reverted Base url to `https://{region}-chronicle.googleapis.com` for all requests
- Dev Base URL to `http://autopush-chronicle.sandbox.googleapis.com`
### Fixed
- Parser extension flakey integration tests

## [0.12.1] - 2025-08-12
### Enhanced
- Base url to `https://chronicle.{region}.rep.googleapis.com` for all requests
- Endpoints to v1 from v1alpha for following:
  - Rule CRUD
  - Reference List CRUD
  - Retro hunt Create & Get

## [0.12.0] - 2025-08-11
### Added
- Native Dashboard Management functionality
  - Create new native dashboard
  - Get dashboard details
  - List dashboards
  - Update existing dashboard
  - Delete a dashboard
  - Duplicate a existing native dashboard
- Dashboard Chart Management functionality
  - Adding new chart to dashboard
  - Getting chart details
  - Editing dashboard chart
  - Removing dashboard chart
- Dashboard query methods
  - Get dashboard query details
  - Execute dashboard query

## [0.11.0] - 2025-08-05
### Added
- Generate UDM key/value mapping from row log

## [0.10.0] - 2025-07-31
### Added
- Parser Extension management functionalities
  - Adding new parser extension
  - Getting parser exetension details
  - Listing parser extensions
  - Activating parser extension
  - Deleting parser extension
### Fixed
- Sub command required for config command in CLI
- `DataTableColumnType` enum to have valid types

## [0.9.0] - 2025-07-29
### Added
- Curated Rule Exclusion (Findings refinement) functionalities
  - Adding new rule exclusion
  - Updating rule exclusion
  - Getting details of specific rule exclusion
  - List rule exclusions
  - Get rule exclusion deployment details
  - Update rule exclusion deployment details
  - Compute rule exclusion (findings refinement) activity


## [0.8.1] - 2025-07-22
### Enhanced:
  - List rules methods to accepts pagination and view scope parameters.
### Fixed:
  - Pagination in list rules to handle nextPageToken correctly.

## [0.8.0] - 2025-07-22
### Added
- Ingestion feed management functionality
  - Adding new ingestion feed
  - Listing existing feeds
  - Getting specific feed details
  - Updating specific feed
  - Deleting specific feed
  - Enabele/Disable ingestion feed
  - Generating secret for http feeds

## [0.7.0] - 2025-07-21
### Enhanced
- Parser ID is optional when running parser against logs, improving usability

## [0.6.6] - 2025-07-15
### Added
- Timeout parameter for query stats

## [0.6.5] - 2025-07-14
### Fixed
- Syntax fixes for f-string

## [0.6.4] - 2025-07-10
### Fixed
- Linter fixes

## [0.6.3] - 2025-07-08
### Added
- Support for impersonated credentials

## [0.6.2] - 2025-06-25
### Fixed
- Optimized `get_or_create_forwarder` function to reduce `list_forwarders` API calls.
  - Implemented caching for the default forwarder ID within the `ChronicleClient` instance.
  - Added a direct `get_forwarder` check for the cached ID before attempting to list all forwarders.
  - This significantly reduces API quota usage when ingesting logs with the default forwarder.

## [0.6.1] - 2025-06-21
### Fixed
- Environment Namespace.

## [0.6.0] - 2025-06-20
### Added
- Added run test rule method and CLI command to execute a test rule.

## [0.5.0] - 2025-06-19
### Added
- Added run parser method and CLI Command

## [0.4.1] - 2025-06-19
### Fixed
- Fixed get_cases bug

## [0.4.0] - 2025-06-17
### Added
- Comprehensive Parser Management functionality for Chronicle log processing
  - Support for creating, retrieving, listing, copying, and deleting parsers
  - Parser activation and deactivation capabilities for managing live parsers
  - Release candidate parser activation for testing new parser versions
  - Force deletion option for removing active parsers when necessary
  - Full integration with Chronicle's Unified Data Model (UDM) transformation pipeline
- Complete CLI support for parser management operations
  - All parser commands available through `secops parser` subcommands
  - Support for parser lifecycle management from command line
  - Integration with existing CLI configuration and authentication
- Enhanced documentation with parser management examples and workflows
  - Updated README.md with comprehensive parser usage examples
  - Added parser management section to CLI.md with practical workflows
  - Clear explanation of parser role in log processing and UDM transformation
  - Connection between parser management and log ingestion processes

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
