import re
import json
import random
from pathlib import Path
from typing import List, Dict, Any, TextIO

INTENT_NAME_REGEX = r'(?<=\*\s).*'
INTENT = 'intent'
QUANTITY = 'quantity'
NECESSARY = 'necessary'
UNNECESSARY = 'unnecessary'
RESPONSES = 'responses'
STORIES_START = '## '
INTENT_START = '* '
RESPONSE_START = ' - '
EMPTY_LINE = '\n'
COMMENT_LINE = '<!--'

INTENT_BUILDER_DEFAULT = {
    INTENT: '',
    QUANTITY: 5,
    NECESSARY: [],
    UNNECESSARY: [],
    RESPONSES: []
}


class Entity:
    def __init__(self, obj: Dict[str, Any]):
        self.name = obj.get('name')
        self.value = obj.get('value')


class IntentBuilder:
    def __init__(self, obj: Dict[str, Any] = INTENT_BUILDER_DEFAULT):
        self.intent: str = obj.get(INTENT)
        self.quantity: int = obj.get(QUANTITY)
        self.necessary: List[Entity] = []
        self.unnecessary: List[Entity] = []
        self.responses: List[str] = []
        for each in obj.get(NECESSARY):
            self.necessary.append(Entity(each))
        for each in obj.get(UNNECESSARY):
            self.unnecessary.append(Entity(each))
        for each in obj.get(RESPONSES):
            self.responses.append(each)

    def build(self, file: TextIO):
        entities = ''
        for entity in self.necessary:
            entities += f'\"{entity.name}\":\"{entity.value}\",'

        if self.unnecessary:
            unnecessary_length = len(self.unnecessary)
            unnecessary_quantity = 1 + random.randrange(unnecessary_length)
            for entity in random.sample(self.unnecessary, k=unnecessary_quantity):
                entities += f'\"{entity.name}\":\"{entity.value}\",'

        if entities:
            file.write(f'{self.intent}{{{entities}}}\n'.replace(',}', '}'))
        else:
            file.write(f'{self.intent}')

        for response in self.responses:
            file.write(f'{response}')


class StoriesBuilder:
    """docstring for StoriesBuilder"""

    def __init__(self, stories_markdown: Path):
        self.intent_builders = []
        with open(stories_markdown, 'r') as stories_file:
            for line in stories_file:
                is_title = STORIES_START in line
                is_intent = INTENT_START in line
                is_comment = line.startswith(COMMENT_LINE)
                is_response = RESPONSE_START in line and not is_title
                is_empty_line = line == EMPTY_LINE
                if not is_comment:
                    if is_title:
                        intent_builder = IntentBuilder()
                    if is_intent:
                        print(line)  # Turn into log
                        intent_builder.intent = line
                    if is_response:
                        intent_builder.responses.append(line)
                    if is_empty_line:
                        self.intent_builders.append(intent_builder)
        print(self.intent_builders)

    def build_stories(self, quantity: int):
        for number in range(quantity):
            builders_size = len(self.intent_builders)
            sample_size = 10 if builders_size > 10 else builders_size
            intents_sample = random.sample(self.intent_builders, k=sample_size)
            with open('stories.md', 'a') as file:
                file.write(f'## generated story {str(number)}\n')
                for intent_builder in intents_sample:
                    intent_builder.build(file)
                file.write(EMPTY_LINE)

    def build_repeated(self):
        for intent_builder in self.intent_builders:
            with open('stories.md', 'a') as file:
                intent_extracted = re.search(INTENT_NAME_REGEX, intent_builder.intent)
                intent_name = intent_extracted.group()
                file.write(f'## generated repeated story {intent_name}\n')
                for __ in range(intent_builder.quantity):
                    intent_builder.build(file)
                file.write(EMPTY_LINE)


stories_builder = StoriesBuilder(Path('mockStories.md'))
stories_builder.build_stories(10)
stories_builder.build_repeated()
