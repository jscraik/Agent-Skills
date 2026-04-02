---
source: https://docs.coderabbit.ai/configuration/example/typescript/expo
---

# Sample Configuration for React Native + Expo

```yaml
# Enables IDE autocompletion for this config file
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json

# Language for CodeRabbit's review comments
language: en

# Enable experimental features (currently not using any specific early_access features)
early_access: true

chat:
  # CodeRabbit will automatically respond to @coderabbitai mentions in PR comments
  auto_reply: true

reviews:
  auto_review:
    # Automatically trigger reviews when PRs are opened or updated
    enabled: true
    # Skip auto-review if PR title contains these keywords
    ignore_title_keywords:
      - "WIP"
    # Don't auto-review draft PRs
    drafts: false
    # Only auto-review PRs targeting these branches
    base_branches:
      - main
      - develop

  # Include a high-level summary at the start of each review
  high_level_summary: true

  # Generate sequence diagrams for complex code flows
  sequence_diagrams: true

  # Don't include poems in reviews (fun feature, but keeping it professional)
  poem: false

  # Show review completion status
  review_status: true

  # Keep the walkthrough section expanded by default
  collapse_walkthrough: false

  # Include summary of all changed files
  changed_files_summary: true

  # Don't automatically request changes on the PR (just leave comments)
  request_changes_workflow: false

  # Pre-merge checks to enforce before merging PRs
  pre_merge_checks:
    description:
      # Validate that PR has a proper description
      mode: warning # Options: off, warning, error
    docstrings:
      # Disable docstring coverage checks (let's assume we don't need them)
      mode: off

  # Exclude these paths from reviews (build artifacts and dependencies)
  path_filters:
    - "!**/node_modules/**" # npm dependencies
    - "!**/android/**" # Native Android build files
    - "!**/ios/**" # Native iOS build files
    - "!**/.expo/**" # Expo build cache
    - "!**/.expo-shared/**" # Expo shared config
    - "!**/dist/**" # Build output

  # Custom review instructions for specific file patterns
  path_instructions:
    # TypeScript/JavaScript files - main app code
    - path: "**/*.{ts,tsx,js,jsx}"
      instructions: |
        Mobile & Expo best practices:
        - Proper use of Expo APIs and hooks (useRouter, useFonts, useAssets)
        - Accessibility: touch targets min 44x44, screen reader support
        - Safe area handling and platform-specific code (iOS vs Android)
        - Memory leaks in useEffect and event listeners

        Performance:
        - Use FlatList/SectionList for lists (never ScrollView with .map)
        - StyleSheet.create instead of inline styles
        - React.memo, useMemo, useCallback where appropriate

        TypeScript:
        - Avoid 'any', use explicit types
        - Prefer 'import type' for type imports

        Security:
        - No exposed API keys or sensitive data
        - Use expo-secure-store for sensitive storage
        - Validate deep linking configurations

        Internationalization:
        - User-visible strings should be externalized to resource files (i18n)

    # Expo app configuration
    - path: "app.json"
      instructions: |
        Review Expo configuration for:
        - Proper app versioning (version and build numbers in sync)
        - Required permissions are justified and minimal
        - Splash screen and icon configurations are complete
        - Deep linking schemes are properly configured
        - EAS build configuration is production-ready
        - No exposed secrets or API keys in configuration

    # EAS (Expo Application Services) build configuration
    - path: "eas.json"
      instructions: |
        Review EAS Build/Submit configuration for:
        - Environment-specific configurations (development, preview, production)
        - Proper credential management
        - Build profiles are optimized for their purpose
        - iOS bundle identifiers and Android package names are correct
        - Distribution settings align with deployment strategy

    # Metro bundler configuration (React Native's JavaScript bundler)
    - path: "metro.config.js"
      instructions: |
        Review Metro bundler configuration for:
        - Asset extensions are properly registered
        - Transformer configuration is optimal for project needs
        - Source map generation is appropriate for environment
        - No security issues with resolver configuration

    # Test files
    - path: "**/*.test.{ts,tsx,js,jsx}"
      instructions: |
        Review test files for:
        - Comprehensive coverage of React Native component behavior
        - Proper use of @testing-library/react-native
        - Mock implementations for Expo modules and native APIs
        - Async behavior is properly tested
        - Accessibility testing is included

    # Asset files (images, fonts, etc.)
    - path: "assets/**/*"
      instructions: |
        Review asset files for:
        - Image optimization (size and format appropriate for mobile)
        - Proper @2x and @3x variants for different screen densities
        - SVG assets are optimized
        - Font files are licensed and optimized
```
