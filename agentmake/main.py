from agentmake import generate
import argparse

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description = """ToolMate AI API client `tm` cli options""")
    # Add arguments
    parser.add_argument("default", nargs="*", default=None, help="prompt")
    parser.add_argument("-b", "--backend", action="store", dest="backend", help="AI backend")
    parser.add_argument("-m", "--model", action="store", dest="model", help="AI model")
    parser.add_argument("-mka", "--model_keep_alive", action="store", dest="model_keep_alive", help="time to keep the model loaded in memory; applicable to ollama only")
    parser.add_argument("-sys", "--system", action='append', dest="system", help="system message")
    parser.add_argument("-con", "--context", action='append', dest="context", help="")
    parser.add_argument("-fup", "--follow_up_prompt", action='append', dest="follow_up_prompt", help="")
    parser.add_argument("-icp", "--input_content_plugin", action='append', dest="input_content_plugin", help="")
    parser.add_argument("-ocp", "--output_content_plugin", action='append', dest="output_content_plugin", help="")
    parser.add_argument("-a", "--agent", action='append', dest="agent", help="")
    parser.add_argument("-t", "--tool", action='append', dest="tool", help="")
    parser.add_argument("-s", "--schema", action='store', dest="schema", help="")
    parser.add_argument("-tem", "--temperature", action='store', dest="temperature", type=float, help="")
    parser.add_argument("-mt", "--max_tokens", action='store', dest="max_tokens", type=int, help="")
    parser.add_argument("-cw", "--context_window", action='store', dest="context_window", type=int, help="")
    parser.add_argument("-bs", "--batch_size", action='store', dest="batch_size", type=int, help="batch size; applicable to ollama only")
    parser.add_argument("-pre", "--prefill", action='append', dest="prefill", help="prefill of assistant message; applicable to deepseek, mistral, ollama and groq only")
    parser.add_argument("-sto", "--stop", action='append', dest="stop", help="stop sequences")
    parser.add_argument("-key", "--api_key", action="store", dest="api_key", help="API key")
    parser.add_argument("-end", "--api_endpoint", action="store", dest="api_endpoint", help="API endpoint")
    parser.add_argument("-pi", "--api_project_id", action="store", dest="api_project_id", help="project id; applicable to Vertex AI only")
    parser.add_argument("-sl", "--api_service_location", action="store", dest="api_service_location", help="cloud service location; applicable to Vertex AI only")
    parser.add_argument("-tim", "--api_timeout", action="store", dest="api_timeout", type=float, help="timeout for API request")
    parser.add_argument("-ww", "--word_wrap", action="store_true", dest="word_wrap", help="wrap output text according to current terminal width")
    # Parse arguments
    args = parser.parse_args()

    #print(args.system)

if __name__ == "__main__":
    test = main()
