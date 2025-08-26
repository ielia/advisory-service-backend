import os

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import Config
from app.models.article import Article
from app.services.hugging_face_service import HuggingFaceService

class MockConfig(Config):
    
    def __init__(self):
        self.CONFIG_FILES = []
        super().__init__()
        self._config = {
        "huggingface.access-token": "token",
        "huggingface.base-url": "https://api-inference.huggingface.co/models/",
        "huggingface.classifier-model": "facebook/bart-large-mnli",
        "huggingface.labelling-model": "baidu/ERNIE-4.5.21B-A3B-PT",
        "huggingface.summarization-model": "Falconsai/text_summarization",
        "huggingface.tagging-model": "openai/gpt-oss-20b:fireworks-ai",
        "huggingface.completions": "https://router.huggingface.co/v1/chat/completions"
        }

config = MockConfig()
hugging_face_service = HuggingFaceService(config)

article = Article(
    full_text="""Scientists Confirm Windows Updates Ignore Humans Out of Professional Obligation
    In a groundbreaking study, researchers revealed that Windows Updates are not inconvenient by accident but due to strict “union rules.” The Association of Forced Restarts (A.F.R.) requires all updates to trigger at least 12 ignored 'Remind Me Later' clicks per day, plus one dramatic reboot during critical Zoom calls.

    Key findings:
    - 87% of updates surveyed admitted they understand “install overnight” perfectly, but prefer “chaotic neutral” as a lifestyle.
    - Restart prompts are secretly a form of psychological dominance.
    - Mac users have filed a complaint, citing “unfair levels of smugness.”

    The research team concludes: humans are allowed to use their computers, but only in brief, legally mandated intervals between security patches.""",
    summary="""Windows Updates intentionally disrupt users under “union rules,” requiring ignored reminders and untimely reboots. Studies show restarts assert dominance, while rival users complain of smugness. Researchers conclude computers are only usable in short gaps between patches."""
)

print(hugging_face_service.add_generated_summary(article))
print(hugging_face_service.add_generated_tags(article))
