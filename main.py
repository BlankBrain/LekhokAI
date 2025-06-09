from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    return {
        "story": f"Generated story for: {data.get('storyIdea', '')} (character: {data.get('character', '')})",
        "imagePrompt": "A beautiful illustration of the story."
    } 