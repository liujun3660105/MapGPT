import asyncio

# from metagpt.roles.tutorial_assistant import TutorialAssistant
from role import TutorialAssistant


async def main():
    topic = "Write a tutorial about MySQL"
    role = TutorialAssistant(language="Chinese")
    await role.run(topic)
    
if __name__ == "__main__":
    asyncio.run(main())