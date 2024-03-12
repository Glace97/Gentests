from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI

import dotenv
dotenv.load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-35-turbo-16k-SSNA",
    model_name="gpt-35-turbo-16k"

)
print("\nAsk GPT without any prompt preparation")
print(llm.invoke("how long is a string?"))