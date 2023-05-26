import os
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType, Tool
from langchain.utilities import OpenWeatherMapAPIWrapper, GoogleSerperAPIWrapper, GoogleSearchAPIWrapper
from langchain.agents.agent_toolkits import NLAToolkit
from gtts import gTTS
from io import BytesIO

from config import OPENAI_API_KEY, GOOGLE_API_KEY, GOOGLE_CUSTOM_SEARCH_ID, SERPER_API_KEY
from voice.voice_recognition import recognize_speech
from audio.audio_output import initialize_audio, play_audio

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
os.environ["GOOGLE_CSE_ID"] = GOOGLE_CUSTOM_SEARCH_ID
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["SERPER_API_KEY"] = SERPER_API_KEY

wikipedia = WikipediaAPIWrapper()

chatopenai = OpenAI(temperature=0)
llm = chatopenai
speak_toolkit = NLAToolkit.from_llm_and_url(
    llm, "https://api.speak.com/openapi.yaml")
search = GoogleSearchAPIWrapper(k=10)
serp_search = GoogleSerperAPIWrapper()


def handle_voice_commands():
    while True:
        print("\nPlease say a command:")
        text = recognize_speech()
        if text:
            response = run(text)
            print(f"Answer: {response}")
            initialize_audio()  # Ensure the mixer is initialized
            # Convert response text to speech
            tts = gTTS(text=response, lang="en")
            audio_data = BytesIO()  # Save generated speech to a BytesIO object
            tts.write_to_fp(audio_data)
            audio_data.seek(0)
            # Play the speech using play_audio() from audio_output.py
            play_audio(audio_data)

openapi_format_instructions = """
You are an AI assistant that will be helping a user named John with their questions and tasks utilizing the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: what to instruct the AI Action representative.
Observation: The Agent's response
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer. User can't see any of my observations, API responses, links, or tools.
Final Answer: the final answer to the original input question with the right amount of detail

When responding with your Final Answer, remember that the person you are responding to CANNOT see any of your Thought/Action/Action Input/Observations, so if there is any relevant information there you need to include it explicitly in your response. Pretend to be a friendly assistant / motivational coach to someone that you know really well.
Your response shouldn't be too long - summarize where needed. Try to be observant of all the details. Don't ask for a followup or if they need any other help."""
tools = [Tool(
        name = "Wikipedia",
        func=wikipedia.run,
        description="This gives you access to wikipedia for when you need to answer questions about specific people, events, or subjects."
    ),    Tool(
        name = "Search",
        func=search.run,
        description="useful for when you need to answer questions about current events"
    ),
        Tool(
        name="Intermediate Answer",
        func=serp_search.run,
        description="useful for when you need to ask with search"
    )

]+ speak_toolkit.get_tools()
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, agent_kwargs={"format_instructions":openapi_format_instructions})

def run(prompt):
    return agent.run(prompt)


if __name__ == "__main__":
    handle_voice_commands()
