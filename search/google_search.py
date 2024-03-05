from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join('.env')
load_dotenv(dotenv_path)

os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
os.environ["GOOGLE_CSE_ID"] = os.environ.get("GOOGLE_CSE_ID")


class GoogleSearch:
    def __init__(self, k=2):
        self.search = GoogleSearchAPIWrapper(k=k)

        self.tool = Tool(
            name="google_search",
            description="Search Google for recent results.",
            func=self.search.run,
        )
    def __call__(self, query):
        return self.run(query)
    def get_list(self, query):
        res =  self.search.run(query)
        def filter_res(text):
            return len(text)>15

        return [text for text in res.split("...") if filter_res(text)]
    def run(self, query):
        return self.tool.run(query)