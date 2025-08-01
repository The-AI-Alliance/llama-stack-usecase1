# README for `01-chatbot`

This project is a demo app providing a quick-start example using [Llama Stack](https://www.llama.com/products/llama-stack/), and two UIs, one built using [chainlit](https://docs.chainlit.io/get-started/overview) and one with [streamlit](https://streamlit.io/).

## Getting Started

We describe two _quick start_ approaches to running this application:
* Docker
* "Native" execution

If you use Linux on a machine with an AMD64-compatible CPU, using the Docker option is the fastest way to try out the application. On other machines or if you use an alternative to Docker, such as Podman, you should use the "native" execution option.

### Quick Start: Docker

For convenient, quick invocation, you can run the app using [Docker](https://www.docker.com/). 

> [!WARNING]
> At this time, we only recommend this approach if you are working on a Linux system with an AMD64-compatible processor. Also, if you are a Podman user, this quick start method uses `docker compose` and `podman compose` doesn't appear to be sufficiently compatible to use as a replacement.

- Install [docker](https://www.docker.com/). You will also need docker compose.

- Copy the environment file and customize it, as needed:
   ```bash
   cp .env.example .env
   ```

- Start all services:
   ```bash
   docker compose up --detach
   ```

- Wait for all services to be healthy (this can take a minute...) and then access the applications in your browser. These are the default ports if you did not customize them in the `.env` file:
   - **Chainlit Chat Interface**: [localhost:9090](http://localhost:9090)
   - **Llama Stack Playground**: [localhost:8501](http://localhost:8501)

### Quick Start: Native Execution

This approach involve more steps, but it works on a broader set of platforms and CPU architectures. We use [`uv`](https://docs.astral.sh/uv/) to manage Python dependencies and run the applications. If you prefer not to use `uv`, manage the dependencies with `pip` or another alternative and remove the `uv run` prefixes shown.

> [!NOTE]
> You may notice that some different port numbers are used in what follows compared to what you'll see in `docker-compose.yml` and the `Dockerfile.*` used above, because some of those ports that are effectively hidden inside containers can collide with common services running on host operating systems, like MacOS.

#### Set Up `uv`

- [Install `uv`](https://docs.astral.sh/uv/)
- Run `uv sync` to install python dependencies. (This will create a `.venv` folder.)

#### Start the `ollama` Server and Download the Llama Model

Start the `ollama` server:

```shell
uv run ollama serve
```
Open a new terminal window and pull down the `llama3.2:1b` model we will use, then verify the list of models contains it:

```shell
uv run ollama pull llama3.2:1b
uv run ollama list
```

The `ollama list` command should contain the `llama:3.2:1b` model.

#### Start the Llama Stack Server

Build and run the server

```shell
ENABLE_OLLAMA=ollama \
OLLAMA_INFERENCE_MODEL=llama3.2:1b \
LLAMA_STACK_PORT=5001 \
uv run --with llama-stack llama stack build \
   --template starter --image-type venv --run
```

> [!WARNING]
> Note that `OLLAMA_INFERENCE_MODEL=llama3.2:1b` doesn't have `ollama/` before the model name. This is the identifier `ollama` expects for the model. In contrast, commands you'll see below use `ollama/llama3.2:1b`, which is the identifier Llama Stack uses.

It can take a moment to come up. It is ready when you see a message like this:

```
INFO:     Uvicorn running on http://['::', '0.0.0.0']:5001 (Press CTRL+C to quit)
```

Open a new terminal window and check that you can get the list of models Llama Stack knows about:

```shell
curl -f http://localhost:5001/v1/models
```

If this works successfully, you'll get some JSON back with the list of models. If you have [`jq`](https://jqlang.org/) installed, piping the output through `jq .` yields this result (and probably other models listed, too):

```
{
   "data": [
      {
         "identifier": "ollama/llama3.2:1b",
         "provider_resource_id": "llama3.2:1b",
         "provider_id": "ollama",
         "type": "model",
         "metadata": {},
         "model_type": "llm"
      }
   ]
}
```

If it appears you connected successfully to the Llama Stack server, but some sort of error was returned, look at the second terminal window where you are running the Llama Stack server and see what errors are reported. For a successful response, you would see something like this:

```
INFO:     ::1:52582 - "GET /v1/models HTTP/1.1" 200 OK
20:35:58.868 [START] /v1/models
20:35:58.871 [END] /v1/models [StatusCode.OK] (2.70ms)
```

#### GUI #1: Llama Stack Playground (Streamlit App)

Now you can run one of two, or perhaps both GUI environments.

First, a GUI app built with [Streamlit](https://streamlit.io/), which is called **Llama Stack Playground** in the docker quick start discussed above, because this example uses a UI that comes with the `llama_stack` distribution. This is why we use a _glob_ in the next command to locate the file inside the `.venv` directory:

```shell
LLAMA_STACK_ENDPOINT=http://localhost:5001 \
uv run --with streamlit,fireworks streamlit run \
   .venv/lib/python3.*/site-packages/llama_stack/distribution/ui/app.py \
   --server.port 8501 --server.address localhost
```

It should pop up a browser window with the GUI at URL `http://localhost:8500`. Select the `ollama/llama3.2:1b` model in the drop down menu. If you don't, you will most likely trigger an exception when you submit a query and the first model in the list is used!

> [!NOTE]
> If you plan to use this GUI regularly, consider installing the `streamlit` and `fireworks` with uv:
> ```shell
> uv add streamlit fireworks
> ```
> Then you can remove `--with streamlit,fireworks` from the previous command.

#### GUI #2: Chainlit Chat Interface

A second GUI environment is a chat app built with [Chainlit](https://docs.chainlit.io/get-started/overview).

```shell
INFERENCE_MODEL=ollama/llama3.2:1b \
LLAMA_STACK_ENDPOINT=http://localhost:5001 \
uv run --with chainlit,fireworks chainlit run demo_01_app.py --host localhost --port 8000
```

> [!NOTE] 
> The model environment variable is specified with the `ollama/` prefix. If you don't specify a model the `demo_01_app` will grab the first LLM returned by the llama stack server, which likely won't work, causing a `500` error to be returned to the browser.

The command should pop up a browser window with the GUI at URL `http://localhost:8000`, where you can enter prompts.

You can also `uv add chainlit fireworks`, etc., if you prefer, as discussed for the first GUI.

### Development Setup

If you used the Docker-based quick start, keep the containers running for what follows. If you used the "native" quick start execution, you'll need to keep the `ollama` and `llama-stack` services running.

Just as we did for the "native" quick start execution above, we'll use [`uv`](https://docs.astral.sh/uv/). [Install `uv`](https://docs.astral.sh/uv/)  if you haven't done this already, then run `uv sync` to install the python dependencies. 

If you don't want to use `uv`, then install the dependencies in `pyproject.toml` another way and omit the `uv run` command prefixes used next.

The `llama-stack-client` CLI is an alternative to the GUI apps. Try a few commands to verify connectivity to the services. First, knowing how to get help is useful. (We won't show the output for the next several commands, but obviously you shouldn't get errors!)

```shell
uv run llama-stack-client --help
```

For details about the sub-commands, e.g., for `models`:

```shell
uv run llama-stack-client models --help
uv run llama-stack-client models list --help
```

> [!TIP]
> If you use a different llama stack server endpoint than the default `http://localhost:5001`, which we are using, then pass the `--endpoint http://server:port` option after `llama-stack-client` and before the sub-commands, `models` in this example. 

Let's try `models list`:

```shell
uv run llama-stack-client models list
```

The content should be the same as the curl command used previously (`curl -f http://localhost:5001/v1/models`), except a nicely-formatted table is printed instead of JSON.

Try an inference call with the client CLI's `inference chat-completion` sub command:

```shell
uv run llama-stack-client \
   inference chat-completion \
   --model-id 'ollama/llama3.2:1b' \
   --message "write a haiku for meta's llama models"
```

Note how the model id is specified, with the `ollama/` prefix. If you omit it, you'll get an error that the model couldn't be found.

You should get output similar to this:

```
INFO:httpx:HTTP Request: POST http://localhost:5001/v1/openai/v1/chat/completions "HTTP/1.1 200 OK"
OpenAIChatCompletion(
    id='chatcmpl-36b421f0-dbf0-4e14-bd60-dbe947f5f0cb',
    choices=[
        OpenAIChatCompletionChoice(
            finish_reason='stop',
            index=0,
            message=OpenAIChatCompletionChoiceMessageOpenAIAssistantMessageParam(
                role='assistant',
                content='Galloping digital\nReflections of the self stare back\nVirtual mystics',
                name=None,
                tool_calls=None,
                refusal=None,
                annotations=None,
                audio=None,
                function_call=None
            ),
            logprobs=None
        )
    ],
    created=1753474963,
    model='llama3.2:1b',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_ollama',
    usage={
        'completion_tokens': 17,
        'prompt_tokens': 34,
        'total_tokens': 51,
        'completion_tokens_details': None,
        'prompt_tokens_details': None
    }
)
```

If you want to try an interactive session, replace the `--message "..."` arguments with `--session`. The prompt will be `>>>`. To exit the loop, use control-d or control-c.

Finally, run the demo client: 

```bash
INFERENCE_MODEL=ollama/llama3.2:1b \
LLAMA_STACK_ENDPOINT=http://localhost:5001 \
uv run demo_01_client.py
```

## Features

- **RAG (Retrieval Augmented Generation)**: The Chainlit app includes document ingestion and RAG capabilities
- **Multiple UIs**: Choose between the official Llama Stack Playground or the custom Chainlit interface
- **Dockerized Setup**: All services run in containers with proper health checks and dependencies
- **Auto Model Pulling**: Ollama automatically pulls the specified model on startup

## Notes

- Tool calling with small models is inconsistent. Sometimes it works sometimes it doesn't. You need to use a bigger model for more consistent results.
- The Chainlit app automatically ingests documents on startup, which may take some time.
- All services use environment variables for configuration - customize via `.env` file.

## Architecture

The project consists of four main services:
1. **Ollama**: Provides local LLM inference
2. **Llama Stack**: API server that interfaces with Ollama
3. **Llama Stack Playground**: Official web UI for testing
4. **Chainlit App**: Custom chat interface with RAG capabilities

In the docker execution option described above, all services are orchestrated via Docker Compose with proper health checks and startup dependencies. The "native execution" alternative shows how to run each service individually and commands to run as health checks.

# TODO

Here are some improvements we are considering. What do you think?

- [ ] Improve demo UI 
   - [ ] Add RAG steps (like [AllyCat](https://github.com/The-AI-Alliance/allycat))
   - [ ] Add AI Alliance branding (like AllyCat)
   - [ ] Explore other UI frameworks (e.g. open-webui)
- [ ] Merge llama-stack-playground with llama-stack container
- [ ] Document Llama Stack issues
    - [ ] undeclared dependencies for client: fire, requests
    - [ ] ollama distribution embedding model name mismatch: `all-MiniLM-L6-v2` vs `all-minilm:latest`
