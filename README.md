[![Supported Python Versions](https://img.shields.io/pypi/pyversions/mujoco-scene-editor)](https://pypi.org/project/mujoco-scene-editor/)
[![PyPI version](https://img.shields.io/pypi/v/mujoco-scene-editor)](https://pypi.org/project/mujoco-scene-editor/)
[![License](https://img.shields.io/pypi/l/mujoco-scene-editor)](https://github.com/markusgrotz/mujoco-scene-editor/blob/main/LICENSE.md)
[![Code style](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)



# Scene Editor for MuJoCo

<p align="center">
   <img src="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/logo.png" width="420" />
</p>

Lightweight, interactive scene editor for [MuJoCo 3.x.](https://mujoco.org/) Create or edit scenes in
your browser to place shapes, import meshes, add robots, and edit elements interactively.


## Quickstart

```bash
pip install mujoco-scene-editor

# Start a fresh, empty scene
mjcreate

# Load from MJCF XML or a blueprint JSON
mjedit path/to/scene.xml
```


## Installation

Install the package on [PyPi](https://pypi.org/project/mujoco-scene-editor/) with

```bash
pip install mujoco-scene-editor
```
This installs necessary dependencies and exposes console scripts.
The following entry points are available and they are also accessible as `scene-editor` subcommands:
 - `mjcreate`: Create an empty scene (opens the web browser)
 - `mjedit`: Edit an existing scene (opens the web browser)
 - `mjprompt`: Generate a scene from a prompt and save it as a MuJoCo XML

From a local checkout:

```bash
pip install -e .
# or with dev tools
pip install -e '.[dev]'
```

To run with uv, use

```bash
# Run the installed console script via uv
uv run scene-editor --help
uv run scene-editor new
```

When the server starts, it prints the URL and opens your browser. Quit with Ctrl+C or the "Quit server" button.

## Examples

Use the provided chemistry lab MJCF as a starting point:

```bash
# With pip-installed package
mjedit examples/prompt/scene_chemistry_lab.xml

# With uv (no install)
uv run --with mujoco-scene-editor mjedit examples/prompt/scene_chemistry_lab.xml
```

Then:
- Use "Add Box/Sphere/Cylinder" to place primitive geoms.
- Use "Add Asset" to insert a local mesh from your file system.
- Drag the gizmo to change pose; use “Export” to write MJCF/JSON.

Robot models are detected using a heuristic. See the section below on how to configure the editor to use different robot models.


## Prompting / Scene Generation Examples

You can conveniently generate a MuJoCo scene from a natural-language prompt using OpenAI or OpenRouter.

You can either export your keys in the shell or place them in a `.env` file in the working directory (or any parent directory). The CLI loads `.env` automatically on startup:

```bash
cp .env.example .env
# Then edit `.env` and set OPENAI_API_KEY=... and/or OPENROUTER_API_KEY=...
```

Exported environment variables take precedence over values in `.env`.

### Using OpenAI

```bash
# Set this to your API key
export OPENAI_API_KEY=...
# Generate a scene from a prompt string
mjprompt "A detailed kitchen."
```

### Using OpenRouter

OpenRouter allows you to use various models beyond OpenAI, including many free models.

```bash
# Set this to your OpenRouter API key
export OPENROUTER_API_KEY=...

# Generate a scene using a specific model via OpenRouter
mjprompt --provider openrouter --model google/gemini-flash-1.5:free "A cozy living room with a sofa and coffee table."

# Verified working example with GPT-5 Codex via OpenRouter
mjprompt --provider openrouter --model openai/gpt-5-codex "Output ONLY a valid MuJoCo XML document with root tag <mujoco> for a red cube on a gray floor."
```

If both `OPENAI_API_KEY` and `OPENROUTER_API_KEY` are set, the editor defaults to OpenAI unless `--provider openrouter` is specified. If only `OPENROUTER_API_KEY` is set, it will automatically fallback to OpenRouter.

Tested OpenRouter models include `openrouter/free`, `openai/gpt-5-codex`, `qwen/qwen3.6-plus:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `openai/gpt-oss-120b:free`, and `openai/gpt-oss-20b:free`. Availability may still vary with your OpenRouter account and privacy settings.

#### Troubleshooting OpenRouter

- If a model returns `404 Not Found`, check your OpenRouter privacy/data policy settings and confirm that the model is enabled for your account.
- Some free models may occasionally return non-MuJoCo XML or malformed output; retrying with a stricter prompt or another tested model such as `openai/gpt-5-codex` usually helps.
- If generation fails entirely, verify that `OPENROUTER_API_KEY` is set correctly in your shell or `.env` file.

To quickly validate your setup, this tested command runs the OpenRouter integration checks:

```bash
set -a && . ./.env && set +a
PYTHONPATH=src uv run pytest -q examples/test_openrouter.py -s
```

Loading a generated scene might not work out of the box in all cases. Generated scenes can have inconsistencies in geometry, but can be easily edited.

### Examples

Below are some generated example scenes. More examples are available in the `examples/prompt` folder.
 
 <table>
   <tr>
     <td align="center">
      <a href="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/prompt/scene_living_room_large.png">
        <img src="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/prompt/scene_living_room_small.png" alt="Living Room" width="420" />
      </a><br/><sub>Living Room</sub>
     </td>
     <td align="center">
      <a href="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/prompt/scene_chess_large.png">
        <img src="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/prompt/scene_chess_small.png" alt="Chess Table" width="420" />
      </a><br/><sub>Chess Table</sub>
     </td>
   </tr>
   <tr>
     <td align="center">
      <a href="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/prompt/scene_playground_large.png">
        <img src="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/prompt/scene_playground_small.png" alt="Playground" width="420" />
      </a><br/><sub>Playground</sub>
     </td>
     <td align="center">
      <a href="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/prompt/scene_chemistry_lab_large.png">
        <img src="https://raw.githubusercontent.com/markusgrotz/mujoco-scene-editor/main/assets/prompt/scene_chemistry_lab_small.png" alt="Chemistry Lab" width="420" />
      </a><br/><sub>Chemistry Lab</sub>
     </td>
   </tr>
 </table>


## Working with different robots or cameras

Robot models must be specified with a JSON configuration.
To work with additional robot models, set the `ROBITS_CONFIG_DIR` environment variable to another config folder. See the [RoBits documentation](https://robits.ai/en/latest/configuration.html) for more details.

```bash
  export ROBITS_CONFIG_DIR=$HOME/code/robits/robits_config/additional_config_sim
  mjedit examples/prompt/scene_coffee_shop.xml
```


## Limitations

- Importing MuJoCo XML files may alter the internal structure, and some tags are discarded.
  - Joints/actuators are discarded if they are not part of a robot description.
  - Additional geom tags, including friction, conaffinity, or contype are not yet supported and discarded.
  - Light/option/compiler elements are not implemented yet.

If you are looking for a robot editor for MuJoCo that supports all the assets please checkout Robola web
  
- Not all MuJoCo robot descriptions have an equivalent URDF representation.

## Links

- Repository: https://github.com/markusgrotz/mujoco-scene-editor
- Issues: https://github.com/markusgrotz/mujoco-scene-editor/issues
