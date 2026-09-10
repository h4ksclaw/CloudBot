SKILLS_URL = "https://github.com/h4ks-com/CloudBot/tree/main/skills"

from cloudbot import hook


@hook.command(autohelp=False)
async def skills():
    """- returns the github url for the skills folder"""
    return SKILLS_URL
