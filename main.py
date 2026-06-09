from fastapi import FastAPI
app=FastAPI(
    title = "Intern Project API",
    description = "My first API application",
    version = "1.0.0"
)

@app.get("/")
def root():
    return {"message":"hello intern"}

@app.get("/health")
def health():
    return {"status":"ok"}