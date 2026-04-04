continue 中的参考配置如下
```yaml
  - name: Gemini 2.5 Flash(gemini-balance)
    provider: gemini
    model: gemini-2.5-flash
    apiKey: sk-123456
    apiBase: http://localhost:8001/gemini/v1beta
    requestOptions:
      headers:
        Content-Type: application/json
```