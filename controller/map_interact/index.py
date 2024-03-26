import asyncio

# from metagpt.roles.tutorial_assistant import TutorialAssistant
from role import GeoAnalysisAssistant


async def main():
    demand = "道路有几种类型"
    role = GeoAnalysisAssistant(language="Chinese")
    await role.run(demand)
    
if __name__ == "__main__":
    asyncio.run(main())