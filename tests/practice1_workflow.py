import asyncio
import os
import subprocess
from flake8.api import legacy as flake8
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import (
    Context,
    Event,
    InputRequiredEvent,
    HumanResponseEvent,
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
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec


class GenCodeEvent(Event):
    pass


class ValidateCodeEvent(Event):
    code: str


class FixCodeEvent(Event):
    code: str
    errors: str


class GenTestCasesEvent(Event):
    pass


class ValidateTestCasesEvent(Event):
    test: str


class GeneratedCodeEvent(Event):
    code: str


class GeneratedTestCasesEvent(Event):
    test: str


class Practice1Flow(Workflow):
    MODEL = 'qwen3-no_think:8b'
    URL = 'http://chipd120.vistcorp.ad.visteon.com:8000/v1'
    API_KEY = os.getenv("VISTEON_OLLAMA_TOKEN")

    @step
    async def setup(self, ctx: Context, ev: StartEvent) -> GenCodeEvent | GenTestCasesEvent:
        print('Setting up...')
        with open(ev.requirements) as reqs_file:
            requirements = reqs_file.read()
        llm = OpenAILike(
            model=self.MODEL, api_base=self.URL, api_key=self.API_KEY, timeout=600,
            is_chat_model=True, is_function_calling_model=True
        )
        mcp_client = BasicMCPClient(
            '.venv/Scripts/python.exe',
            args=[
                "practice1/ai/MCPServers/filesystem_server.py"
            ]
        )
        mcp_tool = McpToolSpec(mcp_client)
        tools = await mcp_tool.to_tool_list_async()
        mcp_client = BasicMCPClient('http://localhost:8585/sse')
        mcp_tool = McpToolSpec(mcp_client)
        tools.extend(await mcp_tool.to_tool_list_async())
        agent = FunctionAgent(
            tools=tools,
            llm=llm,
            system_prompt='You are useful assistant expert in python programming including development and testing.'
        )
        await ctx.set("agent", agent)
        await ctx.set("requirements", requirements)
        ctx.send_event(GenCodeEvent())
        return GenTestCasesEvent()

    @step
    async def gen_code(self, ctx: Context, ev: GenCodeEvent) -> ValidateCodeEvent:
        print('Generating code...')
        code_path = 'llamaindex/output/src/main.py'
        requirements = await ctx.get("requirements")
        agent = await ctx.get("agent")
        query = 'Generate a python script that fulfills the following requirements:\n'\
        f'```\n{requirements}\n```'\
        f'The generated script must be written to file: {code_path}\n'
        await agent.run(query)
        return ValidateCodeEvent(code=code_path)

    @step
    async def validate_code(self, ctx: Context, ev: ValidateCodeEvent) -> GeneratedCodeEvent | FixCodeEvent | GenCodeEvent:
        print('Validating generated code...')
        code_path = ev.code
        if not os.path.exists(code_path):
            return GenCodeEvent()
        style_guide = flake8.get_style_guide(ignore=['E501', 'E305', 'E302'])
        results = style_guide.check_files([code_path])
        errors = results.get_statistics('E')
        if len(errors) == 0:
            return GeneratedCodeEvent(code=code_path)
        else:
            return FixCodeEvent(code=code_path, errors='\n'.join(errors))

    @step
    async def fix_code(self, ctx: Context, ev: FixCodeEvent) -> ValidateCodeEvent:
        print('Fixing generated code errors...')
        code_path = ev.code
        with open(code_path) as code_file:
            code = code_file.read()
        errors = ev.errors
        agent = await ctx.get("agent")
        query = 'In the following script:\n'\
        f'```python\n{code}\n```'\
        'Fix the following errors:\n'\
        f'```\n{errors}\n```'\
        f'The fixed script must be written to file: {code_path}'
        await agent.run(query)
        return ValidateCodeEvent(code=code_path)

    @step
    async def gen_test_cases(self, ctx: Context, ev: GenTestCasesEvent) -> ValidateTestCasesEvent:
        print('Generating test cases...')
        test_path = 'llamaindex/output/test/test_cases.md'
        requirements = await ctx.get("requirements")
        agent = await ctx.get("agent")
        query = 'Generate a markdown file with a test plan to test code that was created to fulfill the '\
        'following requirements:\n'\
        f'```\n{requirements}\n```'\
        'The test steps must contains all details like the expected json content because the requirements '\
        'will not be available for the tester that will follow them.\n'\
        f'The generated script must be written to file: {test_path}'
        await agent.run(query)
        return ValidateTestCasesEvent(test=test_path)

    @step
    async def validate_test_cases(self, ev: ValidateTestCasesEvent) -> InputRequiredEvent | GenTestCasesEvent:
        print('Validating generated test cases...')
        test_cases_path = ev.test
        if not os.path.exists(test_cases_path):
            return GenTestCasesEvent()
        return InputRequiredEvent(test=test_cases_path)

    @step
    async def validate_input(self, ctx: Context, ev: HumanResponseEvent) -> ValidateTestCasesEvent | GeneratedTestCasesEvent:
        response = ev.response
        test_cases_path = ev.test
        if response == 'y' or response == 'yes' or response == '':
            return GeneratedTestCasesEvent(test=test_cases_path)
        else:
            with open(ev.test) as test_file:
                test_plan = test_file.read()
            requirements = await ctx.get("requirements")
            agent = await ctx.get("agent")
            query = 'For the test plan:\n'\
            f'```\n{test_plan}\n```'\
            'Considering the following requirements:\n'\
            f'```{requirements}```\n'\
            f'{response}.\n'\
            f'The updated test plan must be written to file: {test_cases_path}'
            await agent.run(query)
            return ValidateTestCasesEvent(test=test_cases_path)

    @step
    async def test_code(self, ctx: Context, ev: GeneratedCodeEvent | GeneratedTestCasesEvent) -> StopEvent:
        events = ctx.collect_events(ev, [GeneratedCodeEvent, GeneratedTestCasesEvent])
        if not events:
            return None
        print('Testing code...')
        report_path = 'llamaindex/output/report/report.md'
        script_file = events[0].code
        with open(events[1].test) as test_file:
            test_plan = test_file.read()
        agent = await ctx.get("agent")
        query = f'For this script: {script_file}.\n'\
        'Execute all the tests described in the following test plan:\n'\
        f'```\n{test_plan}\n```\n'\
        f'Store the results as a markdown report file located at: {report_path}'
        response = await agent.run(query)
        return StopEvent(result=str(response))


async def main():
    draw_all_possible_flows(Practice1Flow, filename="llamaindex/practice1_flow_all.html")
    w = Practice1Flow(timeout=600, verbose=False)
    handler = w.run(requirements="llamaindex/Requirements.md")
    async for event in handler.stream_events():
        if isinstance(event, InputRequiredEvent):
            print(f'Test Cases generated on {event.test}')
            response = None
            while response != 'y' and response != 'yes' and response != 'n' and response != 'no' and response != '':
                response = input('The test plan is correct? (Y/n):').lower()
            if response == 'n' or response == 'no':
                response = None
                while not response:
                    response = input('Explain what is needed to be changed:').lower()
            handler.ctx.send_event(HumanResponseEvent(response=response, test=event.test))
    draw_most_recent_execution(w, filename="llamaindex/practice1_flow_recent.html")
    final_result = await handler
    print(str(final_result))


if __name__ == "__main__":
    print('Initializing...')
    proc = subprocess.Popen(['python.exe', 'practice1/ai/MCPServers/script_executor_server.py'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    asyncio.run(main())
    proc.terminate()
    proc.wait()
