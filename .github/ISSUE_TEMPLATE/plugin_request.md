---
name: Plugin Request
about: Request a new AI provider plugin for AI-Ticker
title: '[PLUGIN] New plugin for [Provider Name]'
labels: ['plugin', 'enhancement', 'community']
assignees: ''

---

## 🔌 Plugin Information

### Provider Details
- **Provider Name**: [e.g., Anthropic Claude, Google Gemini, etc.]
- **Provider Website**: [URL to provider's website]
- **API Documentation**: [URL to API docs]
- **Pricing Model**: [Free tier/Paid/Credits/etc.]

### API Capabilities
- **Supported Models**: [List of models available]
- **Input Types**: 
  - [ ] Text
  - [ ] Images
  - [ ] Code
  - [ ] Other: [specify]
- **Response Formats**: [JSON, streaming, etc.]
- **Rate Limits**: [If known]

## 🎯 Use Case
**Why would this plugin be valuable?**
Describe the specific benefits this AI provider would bring to AI-Ticker users:
- Unique capabilities
- Cost advantages
- Performance benefits
- Specialized models

## 📋 Plugin Requirements

### Authentication
- **Auth Type**: 
  - [ ] API Key
  - [ ] OAuth
  - [ ] Bearer Token
  - [ ] Other: [specify]
- **Environment Variables Needed**: [list required env vars]

### Configuration
What configuration options should the plugin support?
```yaml
# Example plugin configuration
name: "Provider Name"
version: "1.0.0"
settings:
  api_key:
    type: "string"
    required: true
  model:
    type: "string"
    default: "default-model"
  # Add other settings
```

### Features
Which AI-Ticker features should this plugin support?
- [ ] Stock analysis
- [ ] Market sentiment
- [ ] Price predictions
- [ ] News summarization
- [ ] Technical analysis
- [ ] Other: [specify]

## 🔗 API Examples
If you have experience with this provider's API, share example requests/responses:

<details>
<summary>Example API Call</summary>

```python
# Example API usage
import requests

response = requests.post(
    "https://api.provider.com/v1/chat/completions",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "model": "model-name",
        "messages": [{"role": "user", "content": "Analyze AAPL stock"}]
    }
)
```

</details>

## 📚 Resources
**Helpful resources for implementation:**
- API Documentation: [URL]
- Python SDK: [URL if available]
- Rate Limits: [Documentation URL]
- Pricing: [URL]

## 👥 Community Interest
**Are you willing to help with this plugin?**
- [ ] I can help with development
- [ ] I can help with testing
- [ ] I can provide API access for testing
- [ ] I can help with documentation
- [ ] I'm interested but can't contribute code

## 🔄 Implementation Priority
**How important is this plugin?**
- [ ] High (many users would benefit)
- [ ] Medium (valuable for specific use cases)
- [ ] Low (nice to have)

## 📝 Additional Information
Any other details about this provider or plugin requirements:

---

### Plugin Development Checklist
<!-- For maintainers and contributors -->

- [ ] Research provider API capabilities
- [ ] Create plugin structure
- [ ] Implement authentication
- [ ] Add configuration schema
- [ ] Implement core methods
- [ ] Add error handling
- [ ] Write tests
- [ ] Update documentation
- [ ] Test with real API
- [ ] Submit pull request
