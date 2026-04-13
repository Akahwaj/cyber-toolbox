"""
Mythos Integration module — Anthropic Claude SDK (anthropic>=0.40.0).

Provides a MythosClient class that exposes the full capabilities of Anthropic's
Python SDK within the Mythos Lab Cyber Toolbox:

  • stream_query()        – streaming text responses with live output
  • tool_assisted_scan()  – structured analysis via Claude's tool-use API
  • multi_turn_chat()     – persistent multi-turn conversation session
  • run()                 – interactive menu entry-point

Installation:
    pip install anthropic>=0.40.0

Configuration:
    export ANTHROPIC_API_KEY=your-api-key

API keys are read from the ANTHROPIC_API_KEY environment variable.
"""

import os
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MYTHOS_MODEL = "claude-opus-4-5"

SYSTEM_PROMPT = (
    "You are a cybersecurity expert assistant integrated into the Mythos Lab "
    "Cyber Toolbox. You provide clear, accurate, and ethical guidance on "
    "security topics. Always remind users to work only on systems they own "
    "or have explicit written permission to test."
)

# Tool definitions for structured (tool-use) analysis
_SCAN_TOOLS = [
    {
        "name": "report_findings",
        "description": (
            "Report the structured findings from a cybersecurity analysis. "
            "Always call this tool once to return results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "severity": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low", "informational"],
                    "description": "Overall severity of the findings.",
                },
                "summary": {
                    "type": "string",
                    "description": "One-sentence executive summary.",
                },
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "detail": {"type": "string"},
                            "recommendation": {"type": "string"},
                        },
                        "required": ["title", "detail", "recommendation"],
                    },
                    "description": "List of individual security findings.",
                },
                "next_steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Prioritised list of recommended next steps.",
                },
            },
            "required": ["severity", "summary", "findings", "next_steps"],
        },
    }
]


# ---------------------------------------------------------------------------
# MythosClient
# ---------------------------------------------------------------------------

class MythosClient:
    """
    Thin wrapper around the Anthropic Python SDK that adds cybersecurity-focused
    helpers and gracefully degrades when no API key is configured.

    Usage::

        client = MythosClient()
        # Streaming response
        client.stream_query("What is a SYN flood attack?")
        # Tool-use structured scan
        result = client.tool_assisted_scan("Nginx 1.14.0 with directory listing enabled")
        # Multi-turn session
        client.multi_turn_chat()
    """

    def __init__(self, api_key: str | None = None, model: str = MYTHOS_MODEL):
        self.model = model
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._client: "anthropic.Anthropic | None" = None
        if ANTHROPIC_AVAILABLE and api_key:
            self._client = anthropic.Anthropic(api_key=api_key)

    # ------------------------------------------------------------------
    # Availability helpers
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if the Anthropic client is configured and ready."""
        return self._client is not None

    def _require_client(self) -> bool:
        """Print an error and return False when the client is unavailable."""
        if not ANTHROPIC_AVAILABLE:
            print(
                "\n[Mythos] anthropic package not installed.\n"
                "  Install: pip install anthropic>=0.40.0"
            )
            return False
        if not self._client:
            print(
                "\n[Mythos] ANTHROPIC_API_KEY not set.\n"
                "  Set with: export ANTHROPIC_API_KEY=your-key"
            )
            return False
        return True

    # ------------------------------------------------------------------
    # Core API wrappers
    # ------------------------------------------------------------------

    def stream_query(self, prompt: str, system: str | None = None) -> str:
        """
        Send *prompt* to Claude and stream the response to stdout in real time.

        Returns the complete response text (or an error string).
        """
        if not self._require_client():
            return ""

        system = system or SYSTEM_PROMPT
        print()
        full_text = []
        try:
            with self._client.messages.stream(
                model=self.model,
                max_tokens=2048,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text_chunk in stream.text_stream:
                    print(text_chunk, end="", flush=True)
                    full_text.append(text_chunk)
        except anthropic.APIError as exc:
            error_msg = f"[Mythos API error: {exc}]"
            print(error_msg)
            return error_msg
        print()
        return "".join(full_text)

    def tool_assisted_scan(self, target_description: str) -> dict | None:
        """
        Ask Claude to perform a structured security analysis of *target_description*
        using the tool-use API.  Returns a dict with keys:
          severity, summary, findings (list), next_steps (list).

        Returns None on error or when the client is unavailable.
        """
        if not self._require_client():
            return None

        prompt = (
            f"Perform a security analysis of the following target and call the "
            f"report_findings tool with your results:\n\n{target_description}"
        )
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=_SCAN_TOOLS,
                tool_choice={"type": "any"},
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError as exc:
            print(f"[Mythos API error: {exc}]")
            return None

        for block in response.content:
            if block.type == "tool_use" and block.name == "report_findings":
                return block.input  # type: ignore[return-value]
        return None

    def multi_turn_chat(self) -> None:
        """
        Start an interactive multi-turn conversation session with Claude.
        Type 'exit' or 'quit' to end the session.
        """
        if not self._require_client():
            return

        print("\n💬 Mythos Chat Session  (type 'exit' to quit)")
        print(f"   Model : {self.model}")
        print("-" * 50)

        history: list[dict] = []
        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye.")
                break

            history.append({"role": "user", "content": user_input})
            full_response: list[str] = []

            print("\nMythos: ", end="", flush=True)
            try:
                with self._client.messages.stream(
                    model=self.model,
                    max_tokens=2048,
                    system=SYSTEM_PROMPT,
                    messages=history,
                ) as stream:
                    for chunk in stream.text_stream:
                        print(chunk, end="", flush=True)
                        full_response.append(chunk)
            except anthropic.APIError as exc:
                error = f"[API error: {exc}]"
                print(error)
                full_response = [error]
            print()

            history.append({"role": "assistant", "content": "".join(full_response)})


# ---------------------------------------------------------------------------
# Interactive run() entry-point (called from cyber_toolbox.py menu)
# ---------------------------------------------------------------------------

def run() -> None:
    """Interactive Mythos integration menu."""
    print("\n🔮 Mythos Integration  (Anthropic Claude SDK)")
    print("=============================================")

    client = MythosClient()

    status = "✓ Ready" if client.is_available() else "✗ No API key (offline)"
    print(f"   Model  : {client.model}")
    print(f"   Status : {status}")
    print()
    print("  1. Ask a question  (streaming response)")
    print("  2. Security scan   (tool-use / structured output)")
    print("  3. Chat session    (multi-turn conversation)")
    print("  0. Back")

    choice = input("\nSelect: ").strip()

    if choice == "1":
        prompt = input("\nEnter your question: ").strip()
        if prompt:
            print("\n--- Response ---")
            client.stream_query(prompt)

    elif choice == "2":
        print("\nDescribe the target to analyse.")
        print("Examples:")
        print("  • Apache 2.4.49 web server on Ubuntu 20.04")
        print("  • Android app requesting CAMERA, RECORD_AUDIO, and SMS permissions")
        print("  • SSH port 22 exposed to the internet with password auth enabled\n")
        target = input("Target description: ").strip()
        if not target:
            print("No target provided.")
            return

        print("\n⏳ Analysing with Claude…")
        result = client.tool_assisted_scan(target)

        if result is None:
            print("No results returned.")
            return

        print(f"\n{'='*50}")
        print(f"  Severity : {result.get('severity', 'N/A').upper()}")
        print(f"  Summary  : {result.get('summary', 'N/A')}")
        print(f"{'='*50}")

        findings = result.get("findings", [])
        if findings:
            print(f"\nFindings ({len(findings)}):")
            for i, f in enumerate(findings, 1):
                print(f"\n  [{i}] {f.get('title', 'Untitled')}")
                print(f"      Detail         : {f.get('detail', '')}")
                print(f"      Recommendation : {f.get('recommendation', '')}")

        next_steps = result.get("next_steps", [])
        if next_steps:
            print("\nNext Steps:")
            for step in next_steps:
                print(f"  • {step}")

    elif choice == "3":
        client.multi_turn_chat()

    elif choice == "0":
        return
    else:
        print("Invalid choice.")
