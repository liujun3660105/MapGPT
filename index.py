import asyncio

# from metagpt.roles.tutorial_assistant import TutorialAssistant
# from controller import write-tunior.role
from controller.write_tutorial.role import TutorialAssistant

async def main():
    demand = "Write a tutorial about MySQL"
    role = TutorialAssistant(language="Chinese")
    await role.run(demand)
    
if __name__ == "__main__":
    asyncio.run(main())