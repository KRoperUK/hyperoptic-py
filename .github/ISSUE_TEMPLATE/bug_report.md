name: Bug Report
description: Report a bug or unexpected behavior
labels: ["bug"]
assignees: []

body:

- type: markdown
  attributes:
  value: |
  Thanks for taking the time to fill out this bug report!

- type: textarea
  id: description
  attributes:
  label: Description
  description: Clear and concise description of what the bug is
  placeholder: "Example: When I try to fetch packages, I get an error..."
  validations:
  required: true

- type: textarea
  id: reproduction
  attributes:
  label: Steps to Reproduce
  description: Steps to reproduce the behavior
  value: | 1. Create a client with email/password 2. Call get_packages() 3. See error...
  validations:
  required: true

- type: textarea
  id: expected
  attributes:
  label: Expected Behavior
  placeholder: "Example: Should return a list of packages"
  validations:
  required: true

- type: textarea
  id: actual
  attributes:
  label: Actual Behavior
  placeholder: "Example: Got an APIError with HTTP 500"
  validations:
  required: true

- type: textarea
  id: error_output
  attributes:
  label: Error Output / Stack Trace
  description: Full error message and stack trace if applicable
  render: python

- type: input
  id: python_version
  attributes:
  label: Python Version
  placeholder: "3.11"
  validations:
  required: true

- type: input
  id: library_version
  attributes:
  label: Library Version
  placeholder: "0.1.0"
  validations:
  required: true

- type: textarea
  id: context
  attributes:
  label: Additional Context
  description: Any other context about the problem (environment, API changes, etc.)
