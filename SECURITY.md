# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Council AI, please report it by:

1. **Email**: doron@sonotheia.com
2. **Subject**: "Council AI Security Vulnerability"
3. Include a detailed description of the vulnerability

Please do **not** open a public issue for security vulnerabilities.

## Security Best Practices

### API Keys

- **Never commit API keys** to the repository
- Use environment variables: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- Keep API keys in secure storage
- Rotate keys regularly

### Data Privacy

Council AI sends queries to LLM providers. Be aware:

- Queries are sent to third-party services (Anthropic, OpenAI, etc.)
- Do not include sensitive personal information in queries
- Review your LLM provider's data usage policies
- Consider local/private LLM deployments for sensitive use cases

### Safe Usage

- Validate and sanitize user input before sending to councils
- Implement rate limiting to prevent abuse
- Monitor API usage and costs
- Use the principle of least privilege for API keys

### Dependencies

Council AI has minimal dependencies:

- `pyyaml` - Configuration files
- `pydantic` - Data validation
- `rich` - CLI formatting
- `click` - CLI framework
- `httpx` - HTTP client

Optional dependencies:

- `anthropic` - Anthropic API client
- `openai` - OpenAI API client

All dependencies are from trusted sources and regularly updated.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Known Limitations

1. **LLM Limitations**: Councils rely on LLM capabilities and inherit their limitations
2. **API Rate Limits**: Subject to provider rate limits
3. **Cost Management**: Monitor usage to avoid unexpected costs
4. **Content Filtering**: LLM providers may have content policies

## Security Updates

Security updates will be released as needed. Check:

- GitHub Security Advisories
- Release notes
- CHANGELOG.md

## License

Council AI is released under the MIT License. See LICENSE file for details.
