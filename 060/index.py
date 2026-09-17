from openai import OpenAI
c = OpenAI(api_key=__import__("os").environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
r = c.chat.completions.create(model="deepseek-chat",
    messages=[{"role":"user","content":"37 × 53 等于多少？只回答数字"}], temperature=0)
print("直接问的答案:", r.choices[0].message.content)