## 1.2.2 (2025-04-25)

### Fix

- adjust annotations for KO sequence

## 1.2.1 (2025-04-17)

### Fix

- update KO calculations

### Refactor

- improve testability of search results and improve tests

## 1.2.0 (2025-03-03)

### Feat

- add support for custom message per page

## 1.1.1 (2024-11-07)

### Fix

- update logo

## 1.1.0 (2024-10-30)

### Feat

- add initial implementation of tag sequence search

### Fix

- make sure file_basename is defined when it is used
- indicate which lookup type is used in search errors
- add lookup type to download file name

### Refactor

- clean up data loading for tag resources

## 1.0.1 (2024-05-27)

### Fix

- use search page as start page

## 1.0.0 (2024-05-23)

### Fix

- improve reading experience for very wide screens

## 0.1.0-b0 (2024-05-17)

### Feat

- add http response compression
- add optional view type support in search
- make result list view more configurable
- include anchor links in headers of custom pages
- improve support for large results
- include CHANGELOG in pages
- add support for custom pages
- add initial support for batch searches
- improve sequence visualization
- add crude sequence view
- include all sub parts as separate dataframe columns
- make docker more dev friendly

### Fix

- use aria-label instead of data attribute for annotations
- use ramdom secret key when config is missing
- Allow user to override port with APP_PORT environment variable
- Reintroduce compose file for production, remove aux script
- Small convinience script to start the production environment
- Rearrange
- Make the start script start the production service
- Remove production compose file, rename other compose file
- improve state management for view select
- improve docker production settings
- include static files in dockerfile build
- remove single gene id search in favor of batch search
- ignore empty lines in batch search
- adjust naming of content in csv zip file
- remove spacing introduced with template move
- updated temp logo
- tighten up styling and add temporary logo
- improve use of pageSize in pagination
- adjust spelling mistake in csv-zip content
- remove invalid input indicator from search forms
- make vendor resources project local
- make content styling more consistent
- use the correct order of oligo sequence elements

### Refactor

- clean up usage of mustache templates
- move templates from script to html elements
- copy only required system files to container
- make original algorithm run standalone and share resources with system
- restructure search function
- share common base template
- clean up code structure
