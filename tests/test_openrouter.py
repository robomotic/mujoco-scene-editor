import os
import pytest
import re
import logging
from mujoco_scene_editor.utils.llm import OpenRouterClient, PromptBuilderWrapper

logger = logging.getLogger(__name__)

@pytest.mark.skipif(not os.environ.get("OPENROUTER_API_KEY"), reason="OPENROUTER_API_KEY not set")
def test_openrouter_query():
    client = OpenRouterClient()
    builder = PromptBuilderWrapper()
    builder.add_instruction("Generate a minimal MuJoCo 3.3.7 XML for a red cube.")
    
    # Using a free model for testing
    model = "openrouter/free"
    response = client.query(builder, model=model)
    
    content = response.choices[0].message.content
    assert any(tag in content for tag in ["<mujoco", "<model"]), f"Model {model} failed to generate valid XML tags in response: {content}"
    assert any(tag in content for tag in ["</mujoco>", "</model>"]), f"Model {model} failed to close XML tags in response: {content}"
    
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
