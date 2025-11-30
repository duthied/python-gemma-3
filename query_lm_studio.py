#!/usr/bin/env python3
"""
Query LM Studio for text completions.
"""

import argparse
import os
import sys
import requests
from dotenv import load_dotenv


def load_settings():
    """Load configuration from .env file."""
    load_dotenv()

    required_vars = {
        'LM_STUDIO_HOST': os.getenv('LM_STUDIO_HOST'),
        'LM_STUDIO_PORT': os.getenv('LM_STUDIO_PORT'),
        'LM_STUDIO_MODEL': os.getenv('LM_STUDIO_MODEL')
    }

    # Check for missing variables
    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Please copy .env.example to .env and configure it.", file=sys.stderr)
        sys.exit(1)

    # Convert port to int and validate
    try:
        port = int(required_vars['LM_STUDIO_PORT'])
        if port < 1 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
    except ValueError as e:
        print(f"Error: Invalid LM_STUDIO_PORT - {e}", file=sys.stderr)
        sys.exit(1)

    # Load max_tokens with default fallback
    max_tokens = int(os.getenv('LM_STUDIO_MAX_TOKENS', '100'))

    return {
        'host': required_vars['LM_STUDIO_HOST'],
        'port': port,
        'model': required_vars['LM_STUDIO_MODEL'],
        'max_tokens': max_tokens
    }


def query_lm_studio(prompt, settings, temperature=0.7, max_tokens=100):
    """
    Query LM Studio API for text completion.

    Args:
        prompt: The text prompt to complete
        settings: Dictionary containing host, port, and model
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 100)

    Returns:
        Dictionary with 'text' and 'usage' keys, or None on error
        - text: The completion text
        - usage: Dictionary with prompt_tokens, completion_tokens, total_tokens
    """
    url = f"http://{settings['host']}:{settings['port']}/api/v0/completions"

    payload = {
        "model": settings['model'],
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()

        # Extract the completion text and usage from the response
        if 'choices' in result and len(result['choices']) > 0:
            text = result['choices'][0].get('text', '')
            usage = result.get('usage', {})

            return {
                'text': text,
                'usage': {
                    'prompt_tokens': usage.get('prompt_tokens', 0),
                    'completion_tokens': usage.get('completion_tokens', 0),
                    'total_tokens': usage.get('total_tokens', 0)
                }
            }
        else:
            print("Error: Unexpected response format from API", file=sys.stderr)
            return None

    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to LM Studio at {url}", file=sys.stderr)
        print("Make sure LM Studio is running and accessible.", file=sys.stderr)
        return None
    except requests.exceptions.Timeout:
        print("Error: Request timed out", file=sys.stderr)
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {e.response.status_code} - {e.response.text}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Query LM Studio for text completions.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "The capital of France is"
  %(prog)s "Write a haiku about programming" --temperature 0.9 --max-tokens 200
        """
    )

    parser.add_argument(
        'prompt',
        type=str,
        help='The text prompt to complete'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Sampling temperature (default: 0.7)'
    )

    parser.add_argument(
        '--max-tokens',
        type=int,
        default=None,
        help='Maximum tokens to generate (default: from .env LM_STUDIO_MAX_TOKENS or 100)'
    )

    args = parser.parse_args()

    # Load settings from .env file
    settings = load_settings()

    # Use max_tokens from command line if provided, otherwise from settings
    max_tokens = args.max_tokens if args.max_tokens is not None else settings['max_tokens']

    # Query LM Studio
    print(f"Querying LM Studio with model: {settings['model']}")
    print(f"Prompt: {args.prompt}\n")

    completion = query_lm_studio(
        args.prompt,
        settings,
        temperature=args.temperature,
        max_tokens=max_tokens
    )

    if completion is not None:
        print("Response:")
        print(completion['text'])

        # Display token usage
        usage = completion['usage']
        print("\n---")
        print(f"Token Usage:")
        print(f"  Prompt tokens: {usage['prompt_tokens']}")
        print(f"  Completion tokens: {usage['completion_tokens']}")
        print(f"  Total tokens: {usage['total_tokens']}")
        print(f"  Max tokens (limit): {max_tokens}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
