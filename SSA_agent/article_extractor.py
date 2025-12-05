# action/tools/builtin_tools/advanced_calculus_tool.py
 
from sympy import symbols, sympify, diff, integrate
from sympy.core.sympify import SympifyError
from fairlib.core.interfaces.tools import AbstractTool
 
class ArticleGrabbingTool(AbstractTool):
    """
    ArticleGrabbingTool enables selection of text from json file
    to feed to analyst agent
 
    Supported operations:
    - Grab Text:    grabText(file, count)
 
    Example expressions:
        grabText("harvested_articles.json", 1)
 
    Note:
    - Count represents the article number in the json file
    """
 
    name = "article_grabbing_tool"
    description = (
        "A tool for selecting text from json file."
        "Supports:\n"
        "  - use('next'):    'use('next')'\n"
    )
 
    def __init__(self, file_path: str):
        import json
        self.file_path = file_path
        with open(file_path, "r", encoding="utf-8") as f:
            self.articles = json.load(f)
        self.current_index = 0
 
    def use(self, command: str) -> str:
        """
        Parses and executes article selection commands.
 
        Parameters:
        command (str): The request will be 'next'.
 
        Returns:
        str: The text of the requested article, or an error message.
        """
        try:
            command = command.strip()
 
            if command == "next":
                return self._handle_next()
 
            return "Error: Unsupported command. Use 'next'"
 
        except Exception as e:
            return f"Error: Failed to process request. Details: {e}"
 
    def _handle_next(self) -> str:
        if self.current_index >= len(self.articles):
            return "No more articles available."
 
        article = self.articles[self.current_index]
        self.current_index += 1
        return article.get("text", "No text field found in article.")