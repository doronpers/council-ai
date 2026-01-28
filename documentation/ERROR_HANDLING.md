# Error Handling Guide

Council AI's web application includes a comprehensive error handling system designed to provide clear, actionable feedback to users when things go wrong.

## Overview

The error handling system categorizes errors, provides user-friendly messages, suggests recovery actions, and logs errors for debugging while protecting user privacy. The web app uses typed API error handling (`ApiError`, `classifyError(error: unknown)`), parses API responses as `Record<string, unknown>` with explicit property access, rethrows structured `ApiError` so it is not replaced by generic messages, and logs only safe error shapes (name/message or a placeholder) rather than raw error objects.

## Error Categories

Errors are organized into the following categories:

- **Network Errors**: Connection failures, timeouts, unreachable servers
- **Validation Errors**: Invalid input format, missing required fields, length violations
- **Configuration Errors**: Invalid API keys, missing configuration, invalid base URLs
- **API Errors**: Provider errors, rate limiting, quota exceeded
- **Permission Errors**: Insufficient API key permissions
- **Rate Limiting**: Too many requests, with countdown timers
- **Quota Errors**: API quota exceeded

## Error Message Catalog

All error messages are centralized in `src/council_ai/webapp/src/utils/errorMessages.ts` and include:

- **User-Friendly Message**: Clear explanation of what went wrong
- **Technical Details**: Expandable section with technical information
- **Suggestions**: List of actionable steps to resolve the issue
- **Recovery Actions**: Buttons that perform specific actions (e.g., "Open Settings", "Retry")
- **Severity**: High, medium, or low
- **Recoverable**: Whether the error can be automatically recovered

### Common Error Messages

#### Network Connection Failed

**User Message**: "Unable to connect to the server."

**Suggestions**:

- Check your internet connection
- Verify the server is running
- Try again in a few moments
- Check if you're behind a firewall or proxy

**Recovery Actions**: Retry, Check Diagnostics

#### API Key Invalid

**User Message**: "API key is invalid or expired."

**Suggestions**:

- Verify your API key is correct
- Check if your API key has expired
- Ensure you have sufficient credits/quota
- Try a different API key
- Check your provider's dashboard for key status

**Recovery Actions**: Open Settings, Check Diagnostics

#### Rate Limit Exceeded

**User Message**: "Too many requests. Please wait before trying again."

**Suggestions**:

- Wait a few minutes before retrying
- Consider upgrading your API plan
- Space out your requests
- Use a different provider if available

**Recovery Actions**: Wait and Retry (with countdown timer)

## Inline Validation

Input fields provide real-time validation feedback:

### Query Input

- **Empty Query**: Shows "Query cannot be empty" error
- **Query Too Long**: Shows character count and limit (50,000 characters)
- **Visual Feedback**: Red border and error message below input

### API Key Input

- **Missing API Key**: Shows "API key is required" error
- **Placeholder Detection**: Warns if placeholder values are detected
- **Format Validation**: Validates API key format
- **Success Indicator**: Shows "✓ Valid format" when valid

### Base URL Input

- **Invalid URL Format**: Validates HTTP/HTTPS URL format
- **Unreachable URL**: Checks if server is responding
- **Success Indicator**: Shows "✓ Valid URL format" when valid

### Submit Button

The submit button is disabled when validation errors exist and shows a tooltip explaining why:

- **Single Error**: Shows specific error message
- **Multiple Errors**: Lists all validation errors
- **Hover Tooltip**: Explains disabled state

## Error Display Component

The `ErrorDisplay` component shows errors with:

- **Error Type Icon**: Visual indicator of error category
- **User-Friendly Message**: Prominently displayed
- **Expandable Details**: "What went wrong?" section with technical details
- **Fix Suggestions**: "How to fix" section with actionable steps
- **Recovery Actions**: Buttons for retry, settings, diagnostics
- **Report Issue Link**: Link to GitHub issues for unexpected errors

## Error Recovery Component

The `ErrorRecovery` component provides interactive recovery actions:

- **Retry Button**: Retries the failed operation (with delay for rate limits)
- **Action Buttons**: Context-specific actions (Open Settings, Focus Input, etc.)
- **Quick Fixes**: One-click solutions for common issues
- **Countdown Timers**: For rate limit errors, shows time remaining

### Recovery Actions

Common recovery actions include:

- **Retry**: Retry the failed operation
- **Open Settings**: Scroll to and open configuration section
- **Focus Query Input**: Scroll to and focus query field
- **Focus Base URL Input**: Scroll to and focus base URL field
- **Check Diagnostics**: Open diagnostics panel
- **Switch Provider**: Focus provider selection dropdown

## Progress Dashboard Error Handling

During consultations, the progress dashboard shows:

- **Individual Persona Errors**: Which personas failed and why
- **Error Count**: Total number of errors
- **Error Details**: Expandable error information
- **Cancel Option**: Ability to cancel consultation with confirmation

## Error Logging

Client-side error logging captures:

- **Error Context**: Timestamp, user agent, URL, action, component
- **Error Details**: Error type, message, stack trace
- **User Actions**: Recent user actions leading to error
- **Sanitization**: API keys and sensitive data are redacted

Errors are:

- Logged to browser console
- Stored in localStorage (last 10 errors) for debugging
- Can be exported for support purposes

**Privacy**: All sensitive data (API keys, tokens, credentials) is automatically sanitized before logging.

## Best Practices

### For Users

1. **Read Error Messages**: Error messages are designed to be helpful - read them carefully
2. **Check Suggestions**: Most errors include specific suggestions for resolution
3. **Use Recovery Actions**: Click recovery action buttons for quick fixes
4. **Report Issues**: Use "Report Issue" link for unexpected errors

### For Developers

1. **Use Error Catalog**: Always use centralized error messages from `errorMessages.ts`
2. **Provide Context**: Include relevant context in error messages
3. **Suggest Actions**: Always provide actionable recovery steps
4. **Test Error Paths**: Ensure error handling works for all failure modes
5. **Sanitize Data**: Never log sensitive information

## Troubleshooting

### Common Issues

**"Unable to connect to the server"**

- Check if `council web` is running
- Verify the server is accessible
- Check firewall settings

**"API key is invalid"**

- Verify API key in settings
- Check provider dashboard for key status
- Ensure key has required permissions

**"Rate limit exceeded"**

- Wait for the countdown timer
- Consider upgrading API plan
- Space out requests

**"Base URL unreachable"**

- Verify LM Studio or custom server is running
- Check URL format (should be `http://localhost:PORT/v1`)
- Ensure server is accessible from browser

## Related Documentation

- [Web App Guide](WEB_APP.md) - General web app documentation
- [Configuration Guide](CONFIGURATION.md) - Configuration and API key setup
- [API Reference](API_REFERENCE.md) - Python API error handling
