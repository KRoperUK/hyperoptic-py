name: Feature Request
description: Suggest a new feature or improvement
labels: ["enhancement"]
assignees: []

body:

- type: markdown
  attributes:
  value: |
  Thanks for suggesting a feature! Please provide as much detail as possible.

- type: textarea
  id: description
  attributes:
  label: Description
  description: Is your feature request related to a problem? Please describe it
  placeholder: "Example: I would like to retrieve billing information..."
  validations:
  required: true

- type: textarea
  id: solution
  attributes:
  label: Proposed Solution
  description: Describe the solution you'd like to see
  placeholder: "Example: Add a get_billing() method to HyperopticClient..."
  validations:
  required: true

- type: textarea
  id: alternatives
  attributes:
  label: Alternative Solutions
  description: Describe any alternative solutions you've considered
  placeholder: "Could also expose the raw /billing endpoint..."

- type: textarea
  id: use_case
  attributes:
  label: Use Case
  description: Describe your use case for this feature
  placeholder: "I want to track my monthly bills and display them in my dashboard..."

- type: textarea
  id: context
  attributes:
  label: Additional Context
  description: Any other context about the feature request (API documentation links, examples, etc.)
