# import asyncio
# from acp_sdk.client import Client
# from acp_sdk.models import Message, MessagePart
# import httpx

# API_KEY = "2a6d19343267003dc1a56fdee64b8a3423c49d5f938d8525d605ac27d504e289793b6609752715cb929736b6a40bfedf"
# AGENT_ID = "1bb16d68-d32d-4255-8ec2-04f84b4aff20"

# async def run_test():
#     try:
#         async with Client(
#             base_url="https://app.chicory.ai/v1",
#             auth=("Bearer", API_KEY)
#         ) as client:
#             print("✅ API key accepted. Attempting to reach agent...")

#             try:
#                 run = await client.run_async(
#                     agent=AGENT_ID,
#                     input=[Message(parts=[MessagePart(content="Hello")])]
#                 )
#                 print(f"✅ Agent is accessible. Run ID: {run.run_id}")
#             except httpx.HTTPStatusError as http_err:
#                 print("❌ Agent call failed with HTTP error:")
#                 print(f"Status code: {http_err.response.status_code}")
#                 print(f"Response: {http_err.response.text}")
#             except Exception as e:
#                 print("❌ Agent call failed with unexpected error:")
#                 print(str(e))

#     except Exception as e:
#         print("❌ API key is invalid or failed to connect:")
#         print(str(e))

# if __name__ == "__main__":
#     asyncio.run(run_test())


# import asyncio
# from acp_sdk.client import Client
# from acp_sdk.models import Message, MessagePart

# async def run_async():
#     async with Client(base_url="https://app.chicory.ai/v1", auth=("Bearer", "2a6d19343267003dc1a56fdee64b8a3423c49d5f938d8525d605ac27d504e289793b6609752715cb929736b6a40bfedf")) as client:
#         run = await client.run_async(
#             agent="1bb16d68-d32d-4255-8ec2-04f84b4aff20",
#             input=[Message(parts=[MessagePart(content="Hello")])]
#         )
#         print("Run ID:", run.run_id)
        
#         # Later, retrieve results
#         result = await client.get_run(run.run_id)
#         print(result)

# if __name__ == "__main__":
#     asyncio.run(run_async())

import asyncio
from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart

async def run_async():
    async with Client(base_url="https://app.chicory.ai/v1", auth=("Bearer 2a6d19343267003dc1a56fdee64b8a3423c49d5f938d8525d605ac27d504e289793b6609752715cb929736b6a40bfedf") as client:
        run = await client.run_async(
            agent="1bb16d68-d32d-4255-8ec2-04f84b4aff20",
            input=[Message(parts=[MessagePart(content="Hello")])]
        )
        print("Run ID:", run.run_id)
        
        # Later, retrieve results
        result = await client.get_run(run.run_id)
        print(result)

if __name__ == "__main__":
    asyncio.run(run_async())