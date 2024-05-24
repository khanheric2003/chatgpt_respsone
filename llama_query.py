from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core import QueryBundle

import os
import openai
import json
from llama_index.core import PromptTemplate
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI

# Open secret.json
f = open('secret.json')
data = json.load(f)
OPENAI_API_KEY = data["OPENAI_API_KEY"]
# initialize variables --> should put it inside .secret variable
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
openai.api_key = os.environ["OPENAI_API_KEY"]
loader = WikipediaReader()
# load temp documentations
documents = loader.load_data(pages=['Nikola Tesla','Albert Einstein','Vietnam'])
# store it as indexes
index = VectorStoreIndex.from_documents(documents)

# create query engine with streaming = true
query_engine = index.as_query_engine(
    streaming=True)


# custom prompt templates
qa_prompt_tmpl_str = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the with as much detail as possible and give the source to the question as url ( for example: https:/wikipedia).\n"
    "Query: {query_str}\n"
    "Answer: "
)

'''
Description: generate response from open ai api with customed prompt templates
Args: query:str 

Returns: response:str

'''


async def generate_response(query: str) -> str:
    # set the the prompt template
    qa_prompt_tmpl = PromptTemplate(
        qa_prompt_tmpl_str
    )
    # update query engine with the custom prompt template
    query_engine.update_prompts(
        {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
    )
    # inputting query engine with users query
    streaming_response = query_engine.query(query)
    # custom query engine
    # set initial
    i = 0
    for text in streaming_response.response_gen:
        yield json.dumps(text)
        i += 1
