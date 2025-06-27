import os
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.utils.workflow import (
    draw_all_possible_flows,
    draw_most_recent_execution,
)
from llama_index.llms.openai_like import OpenAILike


class JokeEvent(Event):
    joke: str


class JokeFlow(Workflow):
    MODEL = 'qwen3-no_think:8b'
    API_KEY = os.getenv("VISTEON_OLLAMA_TOKEN")
    llm = OpenAILike(
        model=MODEL, api_base='http://chipd120.vistcorp.ad.visteon.com:8000/v1', api_key=API_KEY, timeout=600,
        is_chat_model=True, is_function_calling_model=True, temperature=0.9
    )

    @step
    async def generate_joke(self, ev: StartEvent) -> JokeEvent:
        topic = ev.topic
        prompt = f"Write your best joke about {topic}."
        response = await self.llm.acomplete(prompt)
        return JokeEvent(joke=str(response))

    @step
    async def critique_joke(self, ev: JokeEvent) -> StopEvent:
        joke = ev.joke
        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        response = await self.llm.acomplete(prompt)
        return StopEvent(result=str(response))


async def main():
    draw_all_possible_flows(JokeFlow, filename="joke_flow_all.html")
    w = JokeFlow(timeout=600, verbose=False)
    result = await w.run(topic="pirates")
    draw_most_recent_execution(w, filename="joke_flow_recent.html")
    print(str(result))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
