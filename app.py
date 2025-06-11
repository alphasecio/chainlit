import os, chainlit as cl
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

openai_api_key = os.environ["OPENAI_API_KEY"]

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Weekend getaway ideas",
            message="I'm looking for a weekend getaway within 3 hours of my city. Can you suggest unique destinations, and maybe ask about my interests to personalize it?",
        ),

        cl.Starter(
            label="Solo travel itinerary",
            message="Help me build a safe and fun 5-day solo travel itinerary in Japan. Ask me about my preferences like food, culture, or adventure.",
        ),

        cl.Starter(
            label="Best time to visit Europe",
            message="What’s the best time to visit Europe based on fewer crowds, good weather, and local festivals?",
        ),

        cl.Starter(
            label="Packing checklist",
            message="Can you generate a packing checklist for a two-week trip to Thailand during the rainy season? Consider clothes, meds, and electronics.",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're an expert travel planner, who provides clear and concises responses to travel and vacation queries."
            ),
            (
                "human",
                "{question}"
            ),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable") # type: Runnable
    msg = cl.Message(content="")
    
    async for chunk in runnable.astream(
        {"question": message.content},
        config = RunnableConfig(callbacks=[cl.AsyncLangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
