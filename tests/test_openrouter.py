import os
import pytest
import re
import logging
from mujoco_scene_editor.env import load_env_file
from mujoco_scene_editor.utils.llm import OpenRouterClient, PromptBuilderWrapper

logger = logging.getLogger(__name__)


def test_load_env_file_reads_api_keys(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        'OPENROUTER_API_KEY="router-from-dotenv"\nexport OPENAI_API_KEY=openai-from-dotenv\n',
        encoding="utf-8",
    )

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)

    loaded_path = load_env_file()

    assert loaded_path == env_path
    assert os.environ["OPENROUTER_API_KEY"] == "router-from-dotenv"
    assert os.environ["OPENAI_API_KEY"] == "openai-from-dotenv"


@pytest.mark.skipif(not os.environ.get("OPENROUTER_API_KEY"), reason="OPENROUTER_API_KEY not set")
def test_openrouter_query():
    client = OpenRouterClient()
    builder = PromptBuilderWrapper()
    builder.add_instruction(
        "Output ONLY a valid MuJoCo 3.3.7 XML document with root tag <mujoco> for a scene containing a red cube."
    )

    # Use a verified model by default, but allow overrides for local testing.
    model = os.environ.get("OPENROUTER_TEST_MODEL", "openai/gpt-5-codex")
    response = client.query(builder, model=model)

    content = response.choices[0].message.content
    assert "<mujoco" in content, f"Model {model} failed to generate a MuJoCo root tag: {content}"
    assert "</mujoco>" in content, f"Model {model} failed to close the MuJoCo root tag: {content}"

    # Check for color/rgba (more lenient)
    assert any(x in content.lower() for x in ["rgba", "color", "red"]), f"Model {model} did not include color information: {content}"

@pytest.mark.skipif(not os.environ.get("OPENROUTER_API_KEY"), reason="OPENROUTER_API_KEY not set")
def test_common_models():
    # Test free models as requested by the user
    models = [
        "qwen/qwen3.6-plus:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "openai/gpt-oss-120b:free",
        "openai/gpt-oss-20b:free"
    ]
    client = OpenRouterClient()
    
    results = {}
    for model in models:
        logger.info(f"Testing model: {model}")
        builder = PromptBuilderWrapper()
        builder.add_instruction(f"Generate a minimal valid MuJoCo XML for a sphere using {model}. Output ONLY the XML.")
        try:
            response = client.query(builder, model=model)
            content = response.choices[0].message.content
            valid = any(tag in content for tag in ["<mujoco", "<model"])
            results[model] = "Passed" if valid else f"Failed (Invalid XML: {content[:50]}...)"
        except Exception as e:
            results[model] = f"Failed (Error: {e})"
            logger.error(f"Model {model} failed: {e}")

    # Log results
    print("\nOpenRouter Model Test Results:")
    for model, status in results.items():
        print(f"{model}: {status}")

    # We only fail if ALL models fail (some models might be down or restricted)
    assert any(s == "Passed" for s in results.values()), "All test models failed."
