from pathlib import Path


def load_prompt(name: str) -> str:
    """
        Load prompt from file.
        :name 提示词文件名
        :return 提示词内容
    """
    prompt_path = Path(__file__).parents[2] / "prompts" / f"{name}.prompt"
    return prompt_path.read_text(encoding="utf-8")
